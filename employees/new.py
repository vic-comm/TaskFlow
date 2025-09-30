import redis
r = redis.from_url('rediss://default:D8wdwZFXSFpcWcU2Y6jvETpXuaVrHKrh@redis-14684.c283.us-east-1-4.ec2.redns.redis-cloud.com:14685')
r.ping()   # should return True