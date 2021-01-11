import pandas as pd
import plotly.graph_objs as go
import requests

# TODO: Scroll down to line 157 and set up a fifth visualization for the data dashboard

def cleandata(countries_iso=['us', 'cn', 'jp', 'de', 'gb', 'in', 'fr', 'br', 'it', 'ca'], \
              date_interval=['1990', '2015']):
    """Clean world bank data for a visualizaiton dashboard

    Keeps data range of dates in keep_columns variable and data for the top 10 economies
    Reorients the columns into a year, country and value
    Saves the results to a csv file

    Args:
        countries_iso (list[str]): iterable of countries iso code: https://www.nationsonline.org/oneworld/country_code_list.htm
        date_interval (list[str]): iterable of data year period
    Returns:
        df (pandas dataframe object): a pandas dataframe object containing clean data

    """
    #TODO: Obtain data from Worldbank's API
    dataset_dict = {'AG.LND.ARBL.HA.PC': 'arable_land_per_person', \
                    'SP.RUR.TOTL.ZS':'rural_percentage', \
                    'SP.RUR.TOTL':'rural_population', \
                    'AG.LND.FRST.K2': 'forest_area_km2'}
    countries_parameter = ';'.join(countries_iso)
    date_start = int(date_interval[0])
    date_end = int(date_interval[1])
    date_parameter = str(date_start) + ':' + str(date_end)
    payload = {'format':'json', 'date':date_parameter, 'per_page':'1000'}

    # Initialize data variable with the intended columns
    data = {'country':[], \
            'year':[]}
    for feature in dataset_dict.values():
        data[feature] = []

    # Requesting from API => parse the data => save to data variable
    for dataset in  dataset_dict.keys():
        # Requesting dataset from API
        data_get = requests.get('http://api.worldbank.org/v2/country/'+ countries_parameter +\
                            '/indicator/' + dataset, params=payload)
        data_get = data_get.json() # Parsing the JSON
        data_get = data_get[1] # Index 1 is where the data reside

        # Parsing JSON data points
        for data_point in data_get:
            country_name = data_point['country']['value']
            year = data_point['date']
            value = data_point['value']
            feature = dataset_dict[dataset]

            # Save to data variable
            data['country'].append(country_name)
            data['year'].append(year)

            # Save value; other features set to be None
            for feature_name in dataset_dict.values():
                if feature_name == feature:
                    data[feature].append(value)
                else:
                    data[feature_name].append(None)

    # Turn into a pandas dataframe
    df = pd.DataFrame(data)
    # Groupby country and year
    df = df.groupby(['country', 'year']).sum().reset_index()
    df['year'] = df['year'].astype('float64')

    return df

def return_figures():
    """Creates four plotly visualizations

    Args:
        None

    Returns:
        list (dict): list containing the four plotly visualizations

    """
    # Initialize data variable
    df = cleandata()

    # first chart plots arable land from 1990 to 2015 in top 10 economies 
    # as a line chart
    
    graph_one = []
    countrylist = df['country'].unique().tolist()
    
    for country in countrylist:
        country_df = df.loc[df['country'] == country]
        x_val = country_df['year'].tolist()
        y_val = country_df['arable_land_per_person'].tolist()

        graph_one.append(
            go.Scatter(
                x = x_val,
                y = y_val,
                mode = 'lines',
                name = country
            )
        )

        layout_one = dict(title = 'Change in Hectares Arable Land <br> per Person 1990 to 2015',\
                          xaxis = dict(title = 'Year',\
                                       autotick=False,\
                                       tick0=1990, dtick=25),
                          yaxis = dict(title = 'Hectares'))

    # second chart plots arable land for 2015 as a bar chart    
    graph_two = []
    df_2015 = df[df['year'] == 2015]
    print(df_2015)
    df_2015.sort_values('arable_land_per_person', ascending=False, inplace=True)

    graph_two.append(
        go.Bar(
            x = df_2015['country'].tolist(),
            y = df_2015['arable_land_per_person'].tolist(),
        )
    )

    layout_two = dict(title = 'Hectares Arable Land per Person in 2015',
                      xaxis = dict(title = 'Country',),
                      yaxis = dict(title = 'Hectares per person'))


    # third chart plots percent of population that is rural from 1990 to 2015
    graph_three = []
    
    for country in countrylist:
        country_df = df.loc[df['country'] == country]
        x_val = country_df['year'].tolist()
        y_val = country_df['rural_percentage'].tolist()

        graph_three.append(
            go.Scatter(
                x = x_val,
                y = y_val,
                mode = 'lines',
                name = country
            )
        )

    layout_three = dict(title = 'Change in Rural Population <br> (Percent of Total Population)',
                        xaxis = dict(title = 'Year', \
                                     autotick=False, \
                                     tick0=1990, \
                                     dtick=25),
                        yaxis = dict(title = 'Percent'))
    
    # fourth chart shows rural population vs arable land
    graph_four = []
    
    # valuevariables = [str(x) for x in range(1995, 2016)]
    # keepcolumns = [str(x) for x in range(1995, 2016)]
    # keepcolumns.insert(0, 'Country Name')

    # df_one = cleandata('data/API_SP.RUR.TOTL_DS2_en_csv_v2_9914824.csv', keepcolumns, valuevariables)
    # df_two = cleandata('data/API_AG.LND.FRST.K2_DS2_en_csv_v2_9910393.csv', keepcolumns, valuevariables)
    
    # df_one.columns = ['country', 'year', 'variable']
    # df_two.columns = ['country', 'year', 'variable']

    for country in countrylist:
      x_val = df[df['country'] == country]['rural_population'].tolist()
      y_val = df[df['country'] == country]['forest_area_km2'].tolist()
      year = df[df['country'] == country]['year'].tolist()
      country_label = df[df['country'] == country]['country'].tolist()

      text = []
      for country, year in zip(country_label, year):
          text.append(str(country) + ' ' + str(year))

      graph_four.append(
          go.Scatter(
              x = x_val,
              y = y_val,
              mode = 'markers',
              text = text,
              name = country,
              textposition = 'top center'
          )
      )

    layout_four = dict(title = 'Rural Population versus <br> Forested Area (Square Km) 1990-2015',
                       xaxis = dict(title = 'Rural Population'),
                       yaxis = dict(title = 'Forest Area (square km)'))

    # fifth chart shows rural population in 2015
    graph_five = []
    df_2015.sort_values('rural_population', ascending=False, inplace=True)

    graph_five.append(
        go.Bar(
            x = df_2015['country'].tolist(),
            y = df_2015['rural_population'].tolist(),
        )
    )

    layout_five = dict(title = 'Rural Population in 2015',
                       xaxis = dict(title = 'Country',),
                       yaxis = dict(title = 'Rural Population'))
    
    # append all charts to the figures list
    figures = []
    figures.append(dict(data=graph_one, layout=layout_one))
    figures.append(dict(data=graph_two, layout=layout_two))
    figures.append(dict(data=graph_three, layout=layout_three))
    figures.append(dict(data=graph_four, layout=layout_four))
    figures.append(dict(data=graph_five, layout=layout_five))

    return figures
