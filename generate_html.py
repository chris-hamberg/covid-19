from SARS_CoV_2_analytics.application import States
import os

states = States()

for state in states:
    path = os.path.join('templates', state.name + '.html')
    #if not os.path.exists(path):
    document = '''{% extends 'base.html' %}
{% block content %}

    <a href="{{ url_for('index') }}"><< INDEX</a>

    <h2>{{ name }}</h2>

    {% for plot in plots %}
        <h3>{{ plot.type }}</h3>
        <img src={{ plot.image }} />
        <br>
    {% endfor %}

{% endblock %}
'''
    with open(path, 'w') as html:
        html.write(document)