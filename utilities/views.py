from rest_framework.views import APIView
from rest_framework.response import Response
# from . import moxa

# 400 = Bad Request
# 401 = Unauthorized
# 422 = Unprocessable Entity.
# 404 = Not found.
# 200 = success 
# 409 = Already Exists 
# 500 = internal server error 

class test(APIView):
    def post(self,request):
        return Response({"hey":"whatsup"},status=200)
     

