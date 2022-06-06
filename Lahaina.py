from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

import requests
import sys
import webbrowser
from googlesearch import search
from selenium.webdriver.common.keys import Keys  # Enables to use RETURN key in searchbox
from urllib.parse import unquote
import time
import re
# define aliases to the color-codes
# import encode
import csv
from datetime import datetime
from datetime import date
import time
import os


class Lahaina(App):
    def build(self):
        # returns a window object with all it's widgets
        self.window = GridLayout()
        self.window.cols = 1
        self.window.size_hint = (0.6, 0.8)
        self.window.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        Window.fullscreen
        # image widget
        self.window.add_widget(Image(source="logo.png",
                                     allow_stretch=True,
                                     keep_ratio=True))

        # label widget
        self.greeting = Label(
            text="Welcome! Please input search keywords.",
            font_size=18,
            color='#00d5ff'
        )
        self.window.add_widget(self.greeting)

        # dataset_type input widget
        # self.window.add_widget(Label(text='Dataset Type', text_size=self.window.size))
        self.window.add_widget(Label(text='Dataset Type'))
        self.dataset_type = TextInput(
            multiline=False,
            # padding_y= (20, 20),
            size_hint=(1, 0.5)
        )
        self.window.add_widget(self.dataset_type)

        # organism input widget
        self.window.add_widget(Label(text='Organism (optional)'))
        self.organism = TextInput(
            multiline=False,
            # padding_y= (20, 20),
            size_hint=(1, 0.5)
        )
        self.window.add_widget(self.organism)

        # add_keywords input widget
        self.window.add_widget(Label(text='Additional Keywords (optional)'))
        self.add_keywords = TextInput(
            multiline=False,
            # padding_y= (20, 20),
            size_hint=(1, 0.5)
        )
        self.window.add_widget(self.add_keywords)

        # button widget
        self.button = Button(
            text="Search",
            size_hint=(1, 0.5),
            bold=True,
            background_color='#00b3ff',
            # remove darker overlay of background colour
            background_normal = ""
        )
        self.button.bind(on_release=self.callback)
        self.window.add_widget(self.button)

        self.output_results = Label(
            text="",
            font_size=16,
            color='#00d5ff'
        )
        self.window.add_widget(self.output_results)

        return self.window

    def find_encode(self):
        print("Finding datasets from ENCODE!")
        # global dataset_type, organism, add_keywords, dataset_type_ready, organism_ready, encode_res, num_of_results_to_display
        encode_res = []
        # Force return from the server in JSON format
        headers = {'accept': 'application/json'}
        user_keywords = self.dataset_type.text + "+" + self.organism.text + "+" + self.add_keywords.text
        user_keywords_no_additionals = self.dataset_type.text + "+" + self.organism.text
        dataset_type_ready = self.dataset_type.text.title()
        organism_ready = self.organism.text.capitalize()
        url = 'https://www.encodeproject.org/search/?type=Experiment&searchTerm=' + user_keywords + '&assay_title=' + dataset_type_ready + '&replicates.library.biosample.donor.organism.scientific_name=' + organism_ready + '&frame=embedded'
        # url = 'https://www.encodeproject.org/search/?type=Experiment&searchTerm=Hi-C+mus+musculus&assay_title=Hi-C&replicates.library.biosample.donor.organism.scientific_name=Mus+musculus&frame=embedded'
        # GET the search result
        response = requests.get(url, headers=headers)
        # Extract the JSON response as a python dictionary
        search_results = response.json()
        # scecond chance if no results at the first attempt. reducing constraints from search url
        if len(search_results['@graph']) == 0:
            url_second = 'https://www.encodeproject.org/search/?type=Experiment&searchTerm=' + user_keywords + '&frame=embedded'
            response = requests.get(url_second, headers=headers)
            search_results = response.json()
        # third chance if no results at the second attempt. removing the additional keywords to allow less constraints
        if len(search_results['@graph']) == 0:
            url_third = 'https://www.encodeproject.org/search/?type=Experiment&searchTerm=' + user_keywords_no_additionals + '&frame=embedded'
            response = requests.get(url_third, headers=headers)
            search_results = response.json()
        count = 0
        num_of_results_to_display = 5  # FI     for res in search_results['@graph']:
            if (dataset_type_ready.lower() in res['assay_title'].lower() or dataset_type_ready.lower() in res['assay_term_name'].lower()) and organism_ready.lower() in res['biosample_summary'].lower():
                new_res = []
                biosample_summary = res['biosample_summary']
                link = "https://www.encodeproject.org" + res['@id']
                date_released = res['date_released']
                new_res.append(biosample_summary)
                new_res.append(link)
                new_res.append(date_released)
                encode_res.append(new_res)
                count = count + 1
                if count == num_of_results_to_display * 2:
                    break
        # Print the object
        # print(json.dumps(search_results, indent=4))
        return encode_res

    def find_geo(self):
        print("Finding datasets from GEO!")
        dataset_type = self.dataset_type.text
        organism = self.organism.text
        add_keywords = self.add_keywords.text
        geo_res = []
        url = "https://www.ncbi.nlm.nih.gov/gds?term=" + dataset_type + " " + organism + " " + add_keywords
        options = webdriver.ChromeOptions()
        options.headless = True
        #driver = webdriver.Chrome(executable_path='D:\user\Documents\Lahaina\chromedriver.exe', options=options)
        #driver = webdriver.Chrome(options=options)
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        driver.get(url)
        content = driver.page_source
        soup = BeautifulSoup(content, "html.parser")
        driver.quit()
        count_elements = 0
        selectors = soup.select('p.title')
        for element in selectors:
            if count_elements > 10:
                break
            title = element.contents[0].text
            link = element.contents[0].attrs["href"]
            link = "https://www.ncbi.nlm.nih.gov" + link
            curr_res = [title, link]
            if curr_res not in geo_res:
                geo_res.append(curr_res)
            count_elements = count_elements + 1

        # df = pd.DataFrame({'Names': geo_res})
        # df.to_csv('geo_res.csv', index=False, encoding='utf-8')
        return geo_res

    def prioritize_geo(self, geo_res):
        dataset_type = self.dataset_type.text
        organism = self.organism.text
        add_keywords = self.add_keywords.text
        global dataset_type_list, organism_list, add_keywords_list
        dataset_type_list = [dataset_type]
        organism_list = [organism]
        add_keywords_list_orig = add_keywords.split()
        add_keywords_list = []
        if '-' in dataset_type:
            titled_no_dash_keyword = dataset_type.title().replace('-', '')
            dataset_type_list.append(titled_no_dash_keyword)
            no_dash_keyword = dataset_type.replace('-', '')
            dataset_type_list.append(no_dash_keyword)  # if keyword contains '-', then add the same keyword w/o '-' because it's common as well
            dataset_type_list.append(no_dash_keyword.capitalize())
            after_hyphen_lower_cased = re.sub(r'(?<=-)\w+', lambda m: m.group().lower(), dataset_type)
            after_hyphen_lower_cased_space_replaces_hyphen = after_hyphen_lower_cased.replace('-',' ')
            space_replaces_hyphen = after_hyphen_lower_cased.replace('-',' ')
            dataset_type_list.append(space_replaces_hyphen)
            dataset_type_list.append(after_hyphen_lower_cased)
            dataset_type_list.append(after_hyphen_lower_cased_space_replaces_hyphen)
        dataset_type_list.append(dataset_type.capitalize())
        dataset_type_list.append(dataset_type.title())

        if '-' in organism:
            no_dash_keyword = organism.replace('-', '')
            organism_list.append(no_dash_keyword)  # if keyword contains '-', then add the same keyword w/o '-' because it's common as well
            organism_list.append(no_dash_keyword.capitalize())
        organism_list.append(organism.capitalize())
        organism_list.append(organism.title())
        for keyword in add_keywords_list_orig:
            add_keywords_list.append(keyword)
            if '-' in keyword:
                no_dash_keyword = keyword.replace('-', '')
                add_keywords_list.append(no_dash_keyword)  # if keyword contains '-', then add the same keyword w/o '-' because it's common as well
                add_keywords_list.append(no_dash_keyword.capitalize())
            add_keywords_list.append(keyword.capitalize())  # each organism in this database appears with capital letter
            add_keywords_list.append(keyword.title())  # each organism in this database appears with capital letter
        for res in geo_res:
            url = res[1]
            options = webdriver.ChromeOptions()
            options.headless = True
            #driver = webdriver.Chrome(executable_path='/Users/Ben/Documents/Python/chromedriver', options=options)
            driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
            driver.get(url)
            content = driver.page_source
            soup = BeautifulSoup(content, "html.parser")
            driver.quit()
            score = 0
            #selectors = soup.select('tr.top')
            for element in soup.findAll("tr", {"valign" : "top"}):
                if 'Title' in element.text:  # check if section 'Title' contains one of the keywords.
                    title_score = 0
                    for dataset_type in dataset_type_list:
                        if dataset_type.lower() in element.text.lower():
                            title_score = title_score + 2
                            break
                    for organism in organism_list:
                        if organism.lower() in element.text.lower():
                            title_score = title_score + 1
                            break
                    for add_keywords in add_keywords_list:
                        if add_keywords.lower() in element.text.lower():
                            title_score = title_score + 1
                    score = score + title_score
                    continue
                if 'Organism' in element.text:  #check if section 'Organism' contains one of the keywords.
                    organisms_score = 0
                    for organism in organism_list:
                        if organism.lower() in element.text.lower():
                            organisms_score = organisms_score + 2
                            break
                    score = score + organisms_score
                    continue
                if 'Summary' in element.text:  # use this mechanism to store result's summary
                    summary = element.text.replace("Summary\n", "")  # remove irrelevant part of the text
                    res.append(summary)
                    summary_score = 0
                    for dataset_type in dataset_type_list:
                        if dataset_type.lower() in element.text.lower():
                            summary_score = summary_score + 2
                            break
                    for organism in organism_list:
                        if organism.lower() in element.text.lower():
                            summary_score = summary_score + 1
                            break
                    for add_keywords in add_keywords_list:
                        if add_keywords.lower() in element.text.lower():
                            summary_score = summary_score + 1
                    score = score + summary_score
                    continue
                if 'Overall design' in element.text: #check if section 'Overall design' contains one of the keywords.
                    overall = element.text.replace("Overall design\n", "")  # remove irrelevant part of the text
                    res.append(overall)
                    overall_score = 0
                    for dataset_type in dataset_type_list:
                        if dataset_type.lower() in element.text.lower():
                            overall_score = overall_score + 3
                            break
                    if overall_score == 0: # if dataset_type does not appear in 'Overall design' section, the search result is not relevant
                        score = 0
                        break
                    for organism in organism_list:
                        if organism.lower() in element.text.lower():
                            overall_score = overall_score + 2
                            break
                    for add_keywords in add_keywords_list:
                        if add_keywords.lower() in element.text.lower():
                            overall_score = overall_score + 2
                    score = score + overall_score
                    continue
                if 'Submission date' in element.text:
                    sub_date = element.text.split('\n')[1]
                    try:
                        date_object = datetime.strptime(sub_date, "%b %d, %Y")
                        date_formated = str(date_object.day) + "/" + str(date_object.month) + "/" + str(date_object.year)
                        res.append(date_formated)
                    except ValueError:
                        pass
                if 'Samples' in element.text:  # check if section 'Samples' contains one of the keywords.
                    samples_score = 0
                    for dataset_type in dataset_type_list:
                        if dataset_type.lower() in element.text.lower():
                            samples_score = samples_score + 4
                            break
                    for organism in organism_list:
                        if organism.lower() in element.text.lower():
                            samples_score = samples_score + 2
                            break
                    for add_keywords in add_keywords_list:
                        if add_keywords.lower() in element.text.lower():
                            samples_score = samples_score + 2
                    score = score + samples_score
                    break  # break since it is the last section that is relevant for score
            res.append(score)
        geo_rest_temp = geo_res.copy()
        for res in geo_rest_temp:
            if len(res) != 6:  # meaning this element has score 0 (does not have date)
                geo_res.remove(res)

    def get_score(self, res):
        return res[5]

    def sort_encode_by_released_date(self, instance, encode_res):
        encode_res.sort(key=lambda x: x[2], reverse=True)
        return encode_res;

    def print_top_res(self, instance, encode_res, geo_res):
        encode_res_sorted_display = []
        geo_res_sorted_display = []
        num_of_results_to_display = 5
        # self.output_title = Label(
        #     text= "ENCODE Results:",
        #     font_size= 16,
        #     color= '#00FFCE'
        # )
        # self.window.add_widget(self.output_title)

        # Prepare ENCODE results for print
        print_count = 0
        print_dataset_type = "Dataset Type: " + self.dataset_type.text
        print_organism = "Organism: " + self.organism.text
        print_add_keywords = "Additional keywords: " + self.add_keywords.text
        encode_res_sorted_display.append(["Search Keywords:"])
        encode_res_sorted_display.append([print_dataset_type])
        encode_res_sorted_display.append([print_organism])
        encode_res_sorted_display.append([print_add_keywords])
        encode_res_sorted_display.append([""])
        encode_res_sorted_display.append([""])
        encode_res_sorted_display.append(["ENCODE Results"])
        encode_res_sorted_display.append(["Biosample Summary", "Link", "Date Released"])
        for res in encode_res:
            # print(f"Result {str(print_count+1)}:\nBiosample Summary: {encode_res[0] : <6}\nDate Released: {encode_res[2] : <6}\nLink: {encode_res[1] : <6}\n\n")
            # res_display = f"Result {str(print_count+1)}:\nBiosample Summary: {encode_res[0] : <6}\nDate Released: {encode_res[2] : <6}\nLink: {encode_res[1] : <6}\n\n"
            # res_display = res_display + "Result " + str(print_count+1) + ":\n" + "Biosample Summary: " + res[0] + "\nDate Released: " + res[2] + "\nLink: " + res[1] + "\n\n"
            encode_res_sorted_display.append(res)
            print_count = print_count + 1
            if print_count == num_of_results_to_display:
                break

        # Prepare GEO results for print
        print_count = 0
        geo_res_sorted_display.append([""])  # Separating between ENCODE and GEO results in CSV file
        geo_res_sorted_display.append([""])
        geo_res_sorted_display.append(["GEO Results"])
        geo_res_sorted_display.append(["Title", "Summary", "Overall design", "Last update date", "Link", "Result Score"])
        for res in geo_res:
            link = res.pop(1)
            res.insert(len(res)-1, link) # insert link before the date
            geo_res_sorted_display.append(res)
            print_count = print_count + 1
            if print_count == num_of_results_to_display:
                break
        current_time = time.strftime("%H_%M_%S")
        date_raw = date.today()
        date_formated = date_raw.strftime("%d-%m-%y")
        search_keywords = self.dataset_type.text + " " + self.organism.text + " " + self.add_keywords.text
        filename = "results-" + search_keywords + "__" + date_formated + "__" + current_time + ".csv"
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(encode_res_sorted_display)
            writer.writerows(geo_res_sorted_display)
        self.output_results = Label(
            text="Results are ready in CSV file!",
            font_size=16,
            color='#00d5ff'
        )
        self.window.add_widget(self.output_results)

    def callback(self, instance):
        # Error handling
        if len(self.dataset_type.text) == 0:
            if self.output_results:
                self.window.remove_widget(self.output_results)
            self.output_results = Label(
                text="Error: Dataset Type is a mandatory field!",
                font_size=16,
                color='#ff5e5e'
            )
            self.window.add_widget(self.output_results)
        else:
            if self.output_results:
                self.window.remove_widget(self.output_results)
            encode_res = self.find_encode()
            geo_res = self.find_geo()
            self.prioritize_geo(geo_res)
            geo_res.sort(key=self.get_score, reverse=True)
            encode_res_sorted = self.sort_encode_by_released_date(self, encode_res)
            self.print_top_res(self, encode_res_sorted, geo_res)



if __name__ == "__main__":
    Lahaina().run()
