from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Category, Location ,Group,Product
from .serializers import CategorySerializer , LocationSerializer ,GroupSerializer,ProductCreateSerializer,ProductViewSerializer,ProductListViewSerializer

class Test(APIView):
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        return x_forwarded_for.split(',')[0].strip()  if x_forwarded_for else request.META.get('REMOTE_ADDR')
    def post(self, request, *args, **kwargs):
        client_ip = self.get_client_ip(request)
        return Response({"client_ip": client_ip})
    
    def get(self, request, *args, **kwargs):
        client_ip = self.get_client_ip(request)
        return Response({"client_ip": client_ip})
    

class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class LocationViewSet(ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

class ProductGroupViewSet(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return ProductListViewSerializer
        elif self.action == "retrieve":
            return ProductViewSerializer
        return ProductCreateSerializer
    
    def get_queryset(self):
        queryset = Product.objects.all()
        
        location_id = self.request.query_params.get("location_id")
        category_id = self.request.query_params.get("category_id")
        group_id = self.request.query_params.get("group_id")
        print( self.request.query_params)
        if location_id: queryset = queryset.filter(location_id=location_id)
        if category_id: queryset = queryset.filter(category_id=category_id)
        if group_id   : queryset = queryset.filter(group_id=group_id)

        return queryset
    
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)