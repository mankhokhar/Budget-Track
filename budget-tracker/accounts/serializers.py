from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import EmailAuthenticatedUser as User, FriendRequest
from wallet.models import CashAccount


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'display_picture']


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'phone_number')
        extra_kwargs = {'password': {'write_only': True}, 'username': {'required': True, 'allow_blank': False},
                        'phone_number': {'required': True}
                        }

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data['username'], validated_data['email'], validated_data['password'],)
        user.phone_number = validated_data['phone_number']
        user.save()
        cashAccount = CashAccount.objects.create(title='Cash', user=user)
        return user


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # The default result (access/refresh tokens)
        data = super(MyTokenObtainPairSerializer, self).validate(attrs)
        # Custom data you want to include
        data.update({'user': UserSerializer(self.user).data})
        # and everything else you want to send in the response
        return data


class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = '__all__'
    user = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)

    def validate(self, data):

        user = User.objects.get(pk=self.initial_data.get('user'))
        receiver = User.objects.get(pk=self.initial_data.get('receiver'))
        if user == receiver:
            raise serializers.ValidationError("Request Sender and Receiver cannot be same")

        if receiver in user.friends.all():
            raise serializers.ValidationError("Already Friends")

        return data

    def create(self, validated_data):
        validated_data['user'] = User.objects.get(pk=self.initial_data.get('user'))
        validated_data['receiver'] = User.objects.get(pk=self.initial_data.get('receiver'))
        request = FriendRequest.objects.create(**validated_data)
        return request

