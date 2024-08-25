from django.shortcuts import render
from rest_framework import generics
from core.models import User, Portfolio
from analysis.models import Asset, PortfolioAsset
from .serializers import UserSerializer, PortfolioSerializer, AssetSerializer, PortfolioAssetSerializer


# Create your views here.
