from src.config.database import Database
import stripe
db = Database()

def first_sub(u_id, current_period_start, current_period_end, subscription_id):
    insert_query = '''INSERT INTO subscriptions (user_id, stripe_subscription_id, current_period_start, current_period_end) VALUES (%s,%s,%s,%s)'''
    db.execute_query(insert_query, (u_id, subscription_id, current_period_start, current_period_end))

def re_sub(u_id, current_period_start, current_period_end, subscription_id):
    update_query = '''UPDATE subscriptions SET current_period_start = %s, current_period_end = %s WHERE user_id = %s AND stripe_subscription_id = %s'''
    db.execute_query(update_query, (current_period_start, current_period_end, u_id, subscription_id))

def delete_sub(u_id, subscription_id):
    update_query = '''UPDATE subscriptions SET auto_renew = false WHERE user_id = %s AND stripe_subscription_id = %s'''
    db.execute_query(update_query, (u_id, subscription_id))

def has_active_subscription(u_id):
    select_query = '''
    SELECT * FROM subscriptions 
    WHERE user_id = %s 
    AND current_period_end > CURRENT_TIMESTAMP
    '''
    res = db.fetch_query(select_query, (u_id,))
    return bool(res)

def expires_at(u_id):
    select_query = '''SELECT current_period_end FROM subscriptions WHERE user_id = %s'''
    res = db.fetch_query(select_query, (u_id,))
    return res[0]['current_period_end']

def get_sub_status(u_id):
    select_query = '''
    SELECT status FROM subscriptions 
    WHERE user_id = %s 
    AND current_period_end > CURRENT_TIMESTAMP
    '''
    res = db.fetch_query(select_query, (u_id,))

    if res and len(res) > 0:
        status = res[0]['status']
        if status == 'active': 
            return 'Premium User'
    return 'Free User'  


def cancel_stripe_subscription(subscription_id):
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
    
def get_sub_id(u_id):
    select_query = '''SELECT stripe_subscription_id FROM subscriptions WHERE user_id = %s '''
    res = db.fetch_query(select_query, (u_id,))
    return res[0]['stripe_subscription_id']






