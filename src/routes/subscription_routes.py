from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from src.db import subscription_db
from src.utils.jwt_handler import get_current_user
from pydantic import BaseModel
from src.db import user_db
import json
import stripe
import os
from src.services.email_service import Emails
from datetime import datetime

stripe.api_version = '2022-08-01'
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
endpoint_secret = os.getenv('WEBHOOK')

router = APIRouter(prefix='/subscribtion', tags=["subscribtion"])
webhook_router = APIRouter(tags=["webhooks"])

class CustomerCreateRequest(BaseModel):
    email: str

class SubscriptionRequest(BaseModel):
    priceId: str

class CancelSubscriptionRequest(BaseModel):
    subscriptionId: str

@router.post('/create-subscription')
async def create_subscription(subscription_data: SubscriptionRequest, u_id: int = Depends(get_current_user)):
    customer_id = user_db.get_customer_id(u_id)
    
    if not customer_id:
        raise HTTPException(status_code=400, detail="Customer not found. Please create customer first.")
    
    price_id = subscription_data.priceId #priceId is created on stripe dashboard for a certain plan need to copy past this to the frontend 
    
    try:
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{
                'price': price_id,
            }],
            payment_behavior='default_incomplete',
            expand=['latest_invoice.payment_intent'],
        )
        
        return {
            "subscriptionId": subscription.id, 
            "clientSecret": subscription.latest_invoice.payment_intent.client_secret
        }#on the frontend clientSecret + stripe component -> webhook gets triggered
        
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": str(e)})
    

@router.post('/cancel-subscription')
async def cancel_subscription(subscription_data: CancelSubscriptionRequest, u_id: int = Depends(get_current_user)):
    try:
        # Cancel the subscription by deleting it
        deleted_subscription = stripe.Subscription.delete(subscription_data.subscriptionId)
        return {
            "success": True,
            "subscription": deleted_subscription,
            "message": "Subscription cancelled successfully"
        }
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
@router.post('/create-customer')
async def create_customer(customer_data: CustomerCreateRequest, u_id:int = Depends(get_current_user)):
    try:
        if user_db.get_customer_id(u_id):
            return {"message":"user already has customer_id"}
        
        customer = stripe.Customer.create(email=customer_data.email)
        user_db.store_customer_id(u_id, customer.id)
        response = JSONResponse(content={"customer": customer})
        return response
        
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.get('/subscriptions')#to list the user their current subscribtion and next billing
async def list_user_subscriptions(u_id: int = Depends(get_current_user)):
    try:
        customer_id = user_db.get_customer_id(u_id)
        
        if not customer_id:
            raise HTTPException(status_code=404, detail="Customer not found")
            
        subscriptions = stripe.Subscription.list(
            customer=customer_id,
            status='all',
            expand=['data.default_payment_method']
        )
        return {"subscriptions": subscriptions}
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")
    
@webhook_router.post('/webhook')
async def webhook_received(request: Request):
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    request_data_bytes = await request.body()
    request_data = json.loads(request_data_bytes)
    
    # Initialize event variable to avoid scope issues
    event = None
    
    if webhook_secret:
        # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
        signature = request.headers.get('stripe-signature')

        try:
            event = stripe.Webhook.construct_event(
                payload=request_data_bytes, sig_header=signature, secret=webhook_secret)
            data = event['data']

        except Exception as e:
            print(f"Webhook signature verification failed: {str(e)}")
            return JSONResponse(content={"error": str(e)}, status_code=400)
        event_type = event['type']
    else:
        data = request_data['data']
        event_type = request_data['type']
        event = request_data  
    
    data_object = data['object']
    
    subscription_id = None
    customer_email = None
    u_id = None
    current_period_start = None
    current_period_end = None

    if event_type == 'invoice.payment_succeeded':
        # Add validation for subscription_id
        subscription_id = data_object.get('subscription')  
        if not subscription_id:
            # Fallback to nested path if needed
            subscription_id = data_object.get('parent', {}).get('subscription_details', {}).get('subscription')
        
        if not subscription_id:
            print("Warning: No subscription ID found in invoice object")
            print(f"Invoice object: {data_object}")
            return JSONResponse(content={'status': 'success', 'message': 'No subscription ID found'})
        
        # Retrieve subscription to get period information
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            current_period_start = datetime.fromtimestamp(subscription.current_period_start)
            current_period_end = datetime.fromtimestamp(subscription.current_period_end)
            print("webhook subscription object content:", subscription)

        except stripe.error.StripeError as e:
            print(f"Error retrieving subscription {subscription_id}: {str(e)}")
            return JSONResponse(content={'status': 'error', 'message': f'Failed to retrieve subscription: {str(e)}'}, status_code=400)
        
        customer_email = data_object.get('customer_email')
        if not customer_email:
            customer_id = data_object.get('customer')
            if customer_id:
                try:
                    customer = stripe.Customer.retrieve(customer_id)
                    customer_email = customer.email
                except stripe.error.StripeError as e:
                    print(f"Error retrieving customer {customer_id}: {str(e)}")
        
        if customer_email:
            u_id = user_db.get_userid(customer_email)
        else:
            print("Warning: No customer email found for subscription")
            return JSONResponse(content={'status': 'error', 'message': 'No customer email found'}, status_code=400)
        
        if data_object['billing_reason'] == 'subscription_create':
            # check if user has active sub
            existing_subs = subscription_db.has_active_subscription(u_id)
            if existing_subs:
                print(f"Duplicate subscription detected for user {u_id}. Canceling new subscription {subscription_id}")

                try:
                    # Cancel the duplicate subscription
                    stripe.Subscription.delete(subscription_id)
                    return JSONResponse(content={'status': 'success', 'message': 'Duplicate subscription canceled'})
                
                except stripe.error.StripeError as e:
                    print(f"Error canceling duplicate subscription: {str(e)}")

            payment_intent_id = data_object.get('payment_intent')
            success_sub = Emails()
            success_sub.subscription_success(customer_email)
            subscription_db.first_sub(u_id, current_period_start, current_period_end, subscription_id)

            if payment_intent_id:
                try:
                    payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
                    stripe.Subscription.modify(
                        subscription_id,
                        default_payment_method=payment_intent.payment_method
                    )
                    print("Default payment method set for subscription:" + payment_intent.payment_method)
                
                except stripe.error.StripeError as e:
                    print(f"Error setting default payment method: {str(e)}")
            else:
                print("Warning: No payment intent ID found")
                
        else:
            # recurring monthly payments
            print(f"Monthly subscription payment succeeded for subscription: {subscription_id}")
            subscription_db.re_sub(u_id, current_period_start, current_period_end, subscription_id) 
            success_sub = Emails()
            success_sub.subscription_renewal(customer_email)
            
    elif event_type == 'invoice.payment_failed':
        # If the payment fails or the customer does not have a valid payment method,
        # an invoice.payment_failed event is sent, the subscription becomes past_due.
        # Use this webhook to notify your user that their payment has
        # failed and to retrieve new card details.
        event_id = event.get('id', 'unknown') if event else 'unknown'
        print(f'Invoice payment failed: {event_id}')
        customer_email = data_object.get('customer_email')

        if not customer_email:
            customer_id = data_object.get('customer')
            if customer_id:

                try:
                    customer = stripe.Customer.retrieve(customer_id)
                    customer_email = customer.email

                except stripe.error.StripeError as e:
                    print(f"Error retrieving customer {customer_id}: {str(e)}")
        
        if customer_email:
            failed_sub = Emails()
            failed_sub.subscription_failed(customer_email)
        
    elif event_type == 'invoice.finalized':
        # If you want to manually send out invoices to your customers
        # or store them locally to reference to avoid hitting Stripe rate limits.
        event_id = event.get('id', 'unknown') if event else 'unknown'
        print(f'Invoice finalized: {event_id}')
        
    elif event_type == 'customer.subscription.deleted':
        # Handle subscription cancelled automatically based
        # upon your subscription settings. Or if the user cancels it.
        event_id = event.get('id', 'unknown') if event else 'unknown'
        print(f'Subscription cancelled: {event_id}')
        subscription_id = data_object.get('id')
        customer_email = data_object.get('customer_email')

        if not customer_email:
            customer_id = data_object.get('customer')
            if customer_id:

                try:
                    customer = stripe.Customer.retrieve(customer_id)
                    customer_email = customer.email

                except stripe.error.StripeError as e:
                    print(f"Error retrieving customer {customer_id}: {str(e)}")
        
        if customer_email:
            u_id = user_db.get_userid(customer_email)
            cancelled_sub = Emails()
            expire_date = subscription_db.expires_at(u_id)
            cancelled_sub.subscription_cancelled(customer_email, expire_date)
            subscription_db.delete_sub(u_id, subscription_id)
        
    else:
        print(f'Unhandled event type: {event_type}')
    
    return JSONResponse(content={'status': 'success'})
