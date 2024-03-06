import redis

r = redis.from_url("redis://red-cnk90oev3ddc7385ngog:6379", decode_responses=True)
r.set('mykey', 'thevalueofmykey')
