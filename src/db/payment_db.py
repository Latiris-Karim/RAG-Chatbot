'''payments table mock up 
id, u_id(fk), subscribtion status(true/false), expires at, auto_renew(no by default, yes on sub,  no on refund or unsub), 
payment_method(paypal or stripe)(maybe not needed), started_at, cancelled at
'''

#functions 
def sub_status(u_id):
    ...

def is_expired(u_id):
    ...
    #call unsubscribe if yes, else return 0

def set_to_subscribed(u_id):
    ...

def set_to_unsubscribed(u_id):
    ...

def check_refund(u_id):
    ... #7days

def check_autorenew(u_id):
    ...
