import pandas as pd
import numpy as np
import re
import lxml
import csv
import os.path

from bs4 import BeautifulSoup
from requests import get

main_url = "https://www.imdb.com"
attributes = ["Name", "Year", "Type", "Genre", "MovieScore", "Metascore", "Duration", "MovieColor", "MovieLanguage", "MovieWorldwideGross", "MovieURL", "Total_Votes"]

if not os.path.exists("fullDataset.csv"):
    with open("fullDataset.csv", "w", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(attributes)

class MainExtract:
    def __init__(self):
        self.initial_data = pd.read_csv("./initial_data.csv", header = None)
        #print(self.initial_data.head())
        print("Initial Data file opened\n")
        page = get(main_url)
        self.soup = BeautifulSoup(page.content, 'lxml')

    def loadAllDetails(self, movie_link):
        rating=0
        totalVotes = 0
        movieType = ""
        genreList = []
        movieMetacritic = 0
        totalTime = 0
        movieColor = ""
        movieLanguage = ""
        movieWorldwideGross = 0
        final_url = main_url + movie_link
        page = get(final_url)
        self.soup = BeautifulSoup(page.content, 'lxml')

        data = self.soup.find(id="pagecontent")

        movieName = str(re.sub(r"\(.*?\)", "", data.find("div", class_="title_wrapper").find("h1").text.strip()))
        print("Movie Name: ", movieName)
        try:
            rating = data.find("span", itemprop="ratingValue").text
            print("Rating: ",rating)
        except:
            print("Unreleased")
            return ["NA", "NA, ""NA", "NA", 0, 0, 0, "NA", "NA", 0, "NA", 0]


        try:
            movieYear = str(re.sub(r"\(.*?\)", "", data.find("div", class_="title_wrapper").find("span", id="titleYear").find("a").text.strip()))
            print("Movie Year: ", movieYear)
        except:
            movieYear = "-"
        totalVotes = int(re.sub(r",", "", data.find("span", itemprop="ratingCount").text))
        print("Total Votes: ", totalVotes)
        movieType = ""
        try:
            #print(data.find("div", class_="subtext").find("a", title="See more release dates").text[:9])
            if (data.find("div", class_="subtext").find("a", title="See more release dates").text[:9] == "TV Series"):
                movieType = "TV Series"
            else:
                movieType = "Movie"
        except:
            pass
        print("Type: ", movieType)
        movieDetails = data.find_all("div", class_="see-more inline canwrap")
        for eachDetail in movieDetails:
            try:
                if (eachDetail.find("h4", class_="inline").text == "Genres:"):
                    genreDetails = eachDetail.find_all("a")
                    for genre in genreDetails:
                        genreList.append(genre.text.strip())
                        #genreList.append(re.sub(r"<.*?>", "", genre))
            except:
                pass
        print("Genre: ", genreList)
        #print(data.find("div", class_="titleReviewBarItem").text)
        try:
            quickLinks = data.find("div", id="quicklinksMainSection").find_all("a")
            for link in quickLinks:
                if link.text == "IMDbPro" :
                    techDetails_url = link.get("href")
            techPage = get(techDetails_url)
            self.soup = BeautifulSoup(techPage.content, 'lxml')
            techData = self.soup.find(id="a-page")
            #print(techData)
            #print(techData.find("div", class_="a-section a-spacing-small gross_world_summary").text)
            movieWorldwideGross = int(re.sub(r",", "", techData.find("div", class_="a-section a-spacing-small gross_world_summary").find("div", class_="a-column a-span5 a-text-right a-span-last").text.strip()[1:]))
            '''
            if (detail.find("h4", class_="inline").text == "Cumulative Worldwide Gross:"):
                print(detail.text)
                #movieWorldwideGross =  int(re.sub(r",", "", detail.text.split(" ")[3][1:-1]))
                print("Movie Worldwide Gross: ", movieWorldwideGross)
            else:
                movieWorldwideGross = 0
            '''
        except:
            movieWorldwideGross = 0
        print("Movie Worldwide GRoss: ", movieWorldwideGross)
        try:
            if "Metascore" in data.find("div", class_="titleReviewBarItem").text:
                movieMetacritic = float(data.find("div", class_="titleReviewBarItem").text.split(" ")[1].strip())
        except:
            movieMetacritic = 0.0
        print("Movie Metascore: ", movieMetacritic)
        details = data.find_all("div", class_="txt-block")
        for detail in details:
            try:
                totalTime = detail.find("time").text
                totalTime = int(totalTime[:-3])
                print("Total time: ", totalTime)
            except:
                pass
            try:
                if (detail.find("h4", class_="inline").text == "Color:"):
                    movieColor = detail.find("a").text
                    print("Movie Color: ", movieColor)
            except:
                pass
            try:
                if (detail.find("h4", class_="inline").text == "Language:"):
                    movieLanguage = detail.find("a").text
                    print("Movie Language: ", movieLanguage)
            except:
                pass

        details = [movieName, movieYear, movieType, genreList, rating, movieMetacritic, totalTime, movieColor, movieLanguage, movieWorldwideGross, final_url, totalVotes]
        return details

    def extractInfo(self):
        print("Extracting Data for each movie....\n")
        len = 0
        if os.path.exists("fullDataset.csv"):
            with open("fullDataset.csv", "r") as readfile:
                len = sum(1 for line in readfile)
            with open("fullDataset.csv", "a", newline="") as csvfile:
                csvwriter = csv.writer(csvfile)
                #for name_year, link in self.initial_data.head().iterrows():
                #for name_year, link in self.initial_data.loc[[169]].iterrows():
                for name_year, link in self.initial_data.iloc[len-1:].iterrows():
                    print("\n",link[0])
                    details = self.loadAllDetails(link[1])
                    if(details[0] != "NA"):
                        csvwriter.writerow(details)


if __name__ == "__main__":
    me = MainExtract()
    me.extractInfo()
