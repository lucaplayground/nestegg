from rest_framework import serializers
from core.models import User, Portfolio
from analysis.models import Asset, PortfolioAsset


# Define serializers for each model
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Only include fields that are necessary for API operations.
        fields = ['id', 'username', 'email', 'currency_code']
        # An extra argument for the password field
        extra_kwargs = {'password': {'write-only': True}}

    # Method for user creation
    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        # Django automatically hashes and password and stores the hash
        user.set_password(validated_data['password'])
        # save the user instance with hashed password
        user.save()
        # return newly created user instance
        return user


class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = '__all__'


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = '__all__'


class PortfolioAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioAsset
        fields = '__all__'