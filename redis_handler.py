import redis

r = redis.Redis(decode_responses=True)
r.set('mykey', 'thevalueofmykey')
