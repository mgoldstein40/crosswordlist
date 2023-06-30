import json
import os
import re
import sys

from bs4 import BeautifulSoup


MONTHS = {
    "January": "01",
    "February": "02",
    "March": "03",
    "April": "04",
    "May": "05",
    "June": "06",
    "July": "07",
    "August": "08",
    "September": "09",
    "October": "10",
    "November": "11",
    "December": "12"
}


def parse_nyt(html_in):
    with open(html_in, "r") as file:
        soup = BeautifulSoup(file, "html.parser")
    xwd_container = soup.find("div", id="crossword-container")


    # DETAILS DATA
    details_data = {}

    details_div = xwd_container.find("div", class_="xwd__details--container")
    author_span, editor_span = details_div.find("div", class_="xwd__details--byline").contents
    
    date = details_div.find(class_="xwd__details--date").string
    day_of_week, date_str = re.split(r", ", date, maxsplit=1)  

    details_data["Title"] = details_div.find(class_="xwd__details--title").string
    details_data["Day of Week"] = day_of_week
    details_data["Date"] = date_str
    details_data["Author"] = author_span.string[3:]
    details_data["Editor"] = editor_span.string[10:]


    # CELLS DATA
    cells = xwd_container("g", class_="xwd__cell")
    width = 15 if len(cells) == 225 else 21 if len(cells) == 441 else None
    if not width:
        raise Exception("The puzzle in {} is not a standard width.".format(html_in))
    
    cells_data = []
    clue_cell_map = {}
    for i in range(len(cells)):
        cell_texts = cells[i]("text", recursive=False)

        cell_value = cell_texts[-1].contents[1] if len(cell_texts) > 0 else "."
        cells_data.append(cell_value)

        if len(cell_texts) == 2:
            clue_id = int(cell_texts[0].contents[1])
            clue_cell_map[clue_id] = i
    

    # CLUES AND ANSWERS DATA
    across_list, down_list = xwd_container("ol", class_="xwd__clue-list--list")
    
    clues_data = {}
    
    for li in across_list:
        clue_id = int(li.find("span", class_="xwd__clue--label").string)
        clue_text = li.find("span", class_="xwd__clue--text").string
        
        curr_cell = clue_cell_map[clue_id]
        stop_cell = (curr_cell // width) * width + width
        answer = ""
        while curr_cell < stop_cell and cells_data[curr_cell] != ".":
            answer += cells_data[curr_cell]
            curr_cell += 1
        if len(answer) < 3:
            raise Exception("The puzzle in {} contains a word that is less than three letters long.".format(html_in))

        clues_data[clue_text] = answer

    for li in down_list:
        clue_id = int(li.find("span", class_="xwd__clue--label").string)
        clue_text = li.find("span", class_="xwd__clue--text").string

        curr_cell = clue_cell_map[clue_id]
        stop_cell = len(cells)
        answer = ""
        while curr_cell < stop_cell and cells_data[curr_cell] != ".":
            answer += cells_data[curr_cell]
            curr_cell += width
        if len(answer) < 3:
            raise Exception("The puzzle in {} contains a word that is less than three letters long.".format(html_in))

        clues_data[clue_text] = answer


    # THE JSON-FORMATTED DICTIONARY THAT WILL BE RETURNED
    json_data = {
        "Details": details_data,
        "Clues": clues_data
    }
    

    # STRING PARSING THE DATE FOR FILE NAMING
    date_str = iter(date_str)
    year = month = day = ""
    while (c := next(date_str)) != " ":
        month += c
    while (c := next(date_str)) != ",":
        day += c
    next(date_str)
    while (c := next(date_str, None)) and c is not None:
        year += c

    month = MONTHS[month]
    if len(day) == 1:
        day = "0" + day


    json_out = "./json/nyt/{}/{}/{}.json".format(year, month, day)
    os.makedirs(os.path.dirname(json_out), exist_ok=True)
    with open(json_out, "w+") as file:
        json.dump(json_data, file, sort_keys=False, indent=2)
    os.remove(html_in)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise Exception("Must include two arguments: the parse type (currently only `nyt` is supported) and the file path.")
    _, parse_type, path = sys.argv
    
    if parse_type != "nyt":
        raise Exception("The only parse type currently supported is for New York Times crosswords (using keyword `nyt`).")
    if os.path.isdir(path):
        sub_files = os.listdir(path)
        for f in sub_files:
            try:
                sub_path = os.path.join(path, f)
                if not os.path.isfile(sub_path):
                    raise Exception("The path {} is a directory, which cannot be parsed since it is not an html file.".format(f))
                if f[-5:] != ".html":
                    raise Exception("The path {} cannot be parsed since it is not an html file.".format(f))
                parse_nyt(sub_path)
            except:
                pass
    elif os.path.isfile(path):
        if path[-5:] != ".html":
            raise Exception("The file {} cannot be parsed since it is not an html file.".format(path))
        parse_nyt(path)
    else:
        raise Exception("Path must be a single html file or a directory that contains only html files.")
