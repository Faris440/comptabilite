from django.shortcuts import render


def handler_400_view(request, exception):
    """ """
    return render(request, "errors/400.html")


def handler_403_view(request, exception):
    """ """
    return render(request, "errors/403.html")


def handler_404_view(request, exception):
    """ """
    return render(request, "errors/404.html")


def handler_500_view(request):
    """ """
    return render(request, "errors/500.html")
