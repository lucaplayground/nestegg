from django.shortcuts import render


# Home view
def HomeView(request):
    return render(request, 'investments/home.html')


# Portfolio view
def PortfolioView(request):
    return render(request, 'investments/portfolio.html')