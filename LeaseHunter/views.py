from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from users.models import House
from users.forms import CommentForm
from .filters import HouseFilter
from bokeh.embed import components
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.transform import jitter
from django.core import serializers
from django.db.models import Count
from geopy.geocoders import Nominatim
import itertools



def index(request):
    '''
    Render Home Page for the website.
    '''
    recom = House.objects.annotate(num_comment=Count('comments')).order_by('-num_comment')[:10]
    recom_for_you = recommend(request)
    recom_for_you_q = House.objects.filter(id__in=[ry.id for ry in recom_for_you]).all()
    r = itertools.chain(recom,recom_for_you_q)
    data = serializers.serialize('json', r, fields=('id','name', 'lat', 'lon'))
    all = House.objects.all()
    heat = serializers.serialize('json', all, fields=('id', 'lat', 'lon', 'rent'))
    return render(request, "home.html", {'selected_house':recom, 'recommended':recom_for_you, 'data':data, 'heat':heat})

def analysis(request):
    '''
    Render analysis page
    '''
    feature_name = request.GET.get('feature')
    feature_names = ["beds", "baths"]
    if feature_name == "baths":
        cats = list(set(House.objects.values_list('baths', flat=True)))
    else:
        feature_name = "beds"
        cats = list(set(House.objects.values_list('beds', flat=True)))
    rent = list(House.objects.values_list('rent', flat=True))
    g = list(House.objects.values_list(feature_name, flat=True))
    data = {'rent': rent,
            'category': g}
    source = ColumnDataSource(data=data)
    cats = sorted(cats)
    p = figure(plot_width=800, plot_height=800, y_range=cats,
               title="Rent by Category")
    p.circle(x='rent', y=jitter('category',  width=0.6, range=p.y_range),alpha=0.3, source=source)
    p.x_range.range_padding = 0
    p.ygrid.grid_line_color = None
    script, div = components(p)
    return render(request, "analysis.html", {'script':script, 'div':div, 'feature_names':feature_names, "current_feature_name":feature_name})

def explore(request):
    '''
    Render Explore Page
    '''
    return render(request, "explore.html")

def search(request):
    '''
    Render Search Page
    '''
    house_list = House.objects.all()
    # page_number = request.GET.get('page')
    house_filter = HouseFilter(request.GET, queryset=house_list)
    response = house_filter.qs
    # paginator = Paginator(house_filter.qs, 10)  # 10 items per page
    # try:
    #     response = paginator.page(page_number)
    # except PageNotAnInteger:
    #     response = paginator.page(1)
    # except EmptyPage:
    #     response = paginator.page(paginator.num_pages)
    all = House.objects.all()
    heat = serializers.serialize('json', all, fields=('id', 'lat', 'lon', 'rent'))
    data = serializers.serialize('json', response, fields=('id','name', 'lat', 'lon'))
    return render(request, "house_result.html", {'filter': response, 'form':house_filter.form, 'heat':heat, 'data':data})


def detail(request):
    '''
    Called when user want to check the detail of a housing source
    '''
    ID = request.POST.get('id')
    house = House.objects.get(id=ID)
    isCreator = house.created_by == request.user
    commet_form = CommentForm()
    like = request.user.profile.favorites.filter(id=ID).exists()
    return render(request, "single_house.html", {'house':house, 'is_creator':isCreator, 'comment_form':commet_form, 'like':like})

def recommend(request):
    '''
    Give recommendation for housing sources based on number of comments/favorites
    If logged in, also give recommendation based on user favorites.
    '''
    if request.user:
        if request.user.profile.favorites:
            favorites = request.user.profile.favorites.all()
            cities = [h.city for h in favorites]
            c = max(set(cities), key=cities.count)
            beds = [h.beds for h in favorites]
            br = max(set(beds), key=beds.count)
            baths = [h.baths for h in favorites]
            ba = max(set(baths), key=baths.count)
            house_list = House.objects.filter(city=c, beds=br,baths=ba).all()
            favorites = favorites.filter(city=c, beds=br,baths=ba).all()
            ordered = sorted(house_list, key=lambda h: calculate_dist(h, favorites))
            return ordered[:5]
    else:
        return None


def calculate_dist(h1, favorites):
    tot = 0
    for f in favorites:
        tot += abs(h1.lat-f.lat) + abs(h1.lon-f.lon)
    return -tot