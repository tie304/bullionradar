from bs4 import BeautifulSoup


def determine_metal_type(data_query):
    gold_instances = 0
    silver_instances = 0
    title = data_query['title'].lower()
    description = data_query['description'].lower()

    title_silver = [i for i in range(len(title)) if title.startswith("silver", i)]
    description_silver = [i for i in range(len(description)) if title.startswith("silver", i)]
    title_gold = [i for i in range(len(title)) if title.startswith("gold", i)]
    description_gold = [i for i in range(len(description)) if title.startswith("gold", i)]

    silver_instances += len(title_silver)
    silver_instances += len(description_silver)
    gold_instances += len(title_gold)
    gold_instances += len(description_gold)

    if gold_instances > silver_instances:
        return "gold"
    elif silver_instances > gold_instances:
        return "silver"
    elif silver_instances == gold_instances:
        return "unknown"

def determine_metal_form(data_query):
    coin_instances = 0
    bar_instances = 0

    title = data_query['title'].lower()
    description = data_query['description'].lower()

    bar_title = [i for i in range(len(title)) if title.startswith("bar", i)]
    description_bar = [i for i in range(len(description)) if title.startswith("bar", i)]
    title_coin = [i for i in range(len(title)) if title.startswith("coin", i)]
    description_coin = [i for i in range(len(description)) if title.startswith("coin", i)]

    bar_instances += len(bar_title)
    bar_instances += len(description_bar)
    coin_instances += len(title_coin)
    coin_instances += len(description_coin)

    if coin_instances > bar_instances:
        return "coin"
    elif bar_instances > coin_instances:
        return "bar"
    elif bar_instances == coin_instances:
        return "unknown"

def determine_metal_size(data_query):
    # TODO work in progress
    sizes = ["oz", "g", "kg"]
    title_description = data_query['title'] + data_query['description'].lower()

    oz_starts = len([i for i in range(len(title)) if title.startswith("oz", i)])
    kg_start = len([i for i in range(len(title)) if title.startswith("kg", i)])
    g_start = len([i for i in range(len(title)) if title.startswith("g", i)])






def parse_price_to_float(price: str) -> float:
    cleaned_str = ""
    for char in price:
        if char == "." or char.isdigit():
            cleaned_str += char
    return float(cleaned_str)


def extract_templates(data, job):

    """
    Looks through templates  and extracts data
    """
    soup = BeautifulSoup(data, features="html.parser")
    data_query = {}
    for template in job['templates']:
        data_query[template] = {}
        for data_point, data in job['templates'][template].items():
            selector = data.get("selector")
            meta_selector = data.get("meta_selector")
            if selector:
                bs4_selector = soup.select(selector)
                selector_strategy = data.get("selector_strategy")
                selector_type = data.get("selector_type")
                if selector_strategy == "not_exists" and bs4_selector:
                    data_query[template][data_point] = False
                elif selector_strategy == "not_exists" and not bs4_selector:
                    data_query[template][data_point] = True
                elif selector_strategy == "exists" and not bs4_selector:
                    data_query[template][data_point] = False
                elif selector_strategy == "exists" and bs4_selector:
                    data_query[template][data_point] = True

                elif selector_strategy == "should_exist" and not bs4_selector:
                    pass
                elif selector_strategy == "should_exist" and bs4_selector:
                    if selector_type == "string":
                        data_query[template][data_point] = bs4_selector[0].text.strip()
                    elif selector_type == "float":
                        data_query[template][data_point] = parse_price_to_float(bs4_selector[0].text.strip())
    for t in job['templates']:
        for k in job['templates'][t]:
            if k not in data_query[t].keys():
                data_query.pop(t)
                break
    if data_query:
        return data_query