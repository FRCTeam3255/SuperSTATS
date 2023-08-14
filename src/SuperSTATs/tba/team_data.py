import streamlit as st
import pandas as pd
import tbapy

tba = tbapy.TBA(st.secrets["TBA_API"])

# https://github.com/frc1418/tbapy
# from SuperSTATs.tba.team_data import *

def team_info(team):
    return tba.team(f'frc{team}', True)

def robots(team):
    info = tba.team_robots(f'frc{team}')
    for robot in info:
        print(robot['year'], robot['robot_name'])

def media(team, year):
    info = tba.team_media(f'frc{team}', year)
    for output in info:
        print(output)
    
def awards(team, year):
    info = tba.team_awards(f'frc{team}', year)
    for output in info:
        print(output)

def get_team(team, year):
    print(f'\n[TEAM {team} : {year} YEAR]')
    team_info(team)
    print('\n[ROBOTS]')
    robots(team)
    print('\n[MEDIA]')
    media(team, year)
    print('\n[AWARDS]')
    awards(team, year)