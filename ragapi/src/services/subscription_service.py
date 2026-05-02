import stripe


def cancel_stripe_subscription(subscription_id: str):
    try:
        deleted_subscription = stripe.Subscription.delete(subscription_id)
        return {
            "success": True,
            "subscription": deleted_subscription,
            "message": "Subscription cancelled successfully"
        }
    except stripe.error.StripeError as e:
        print(f"Stripe error: {str(e)}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        print(f"Error canceling subscription: {str(e)}")
        return {"success": False, "error": str(e)}
