import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import click
import pandas as pd
from datetime import datetime
import logging

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')


@click.group()
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)
    ctx.obj['HEADERS'] = ({'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    ctx.obj['driver'] = webdriver.Chrome("/Users/goodwinm/OurStuff/Matt/DS/DS_Projects/chromedriver", options=options)


@cli.command()
@click.option('--site-file', default=None, required=True)
@click.option('--output-file', default=None, required=True)
@click.pass_context
def price_parser(ctx, site_file, output_file):
    """
    Parse prices for different urls
    """

    # read in list of websites to look up
    logging.info(f'Reading in urls from {site_file} to look up prices...')
    site_df = pd.read_csv(site_file)

    # if output file already exists then read it in, otherwise create new data frame
    try:
        output_df = pd.read_csv(output_file)
    except FileNotFoundError:
        output_df = pd.DataFrame(columns=['Description', 'Date', 'Price'])

    # get today's date
    date_pulled = datetime.today().strftime('%Y-%m-%d')

    # loop through each website
    for i in range(site_df.shape[0]):

        # get price depending on site
        if site_df['site'].iloc[i].lower() == 'amazon':
            logging.info(f"For {site_df['description'].iloc[i]} reading in site {site_df['url'].iloc[i]} from Amazon")
            # request url content
            page = requests.get(site_df['url'].iloc[i], headers=ctx.obj['HEADERS'])
            # parse html
            soup = BeautifulSoup(page.content, 'html.parser')
            # get price and put into float
            price = soup.find(id='priceblock_ourprice').get_text()
            price = float(price[1:])

        elif site_df['site'].iloc[i].lower() == 'home depot':
            logging.info(f"For {site_df['description'].iloc[i]} reading in site {site_df['url'].iloc[i]} from Home Depot")
            # get driver
            driver = ctx.obj['driver']
            driver.get(site_df['url'].iloc[i])
            # get price and put into float
            price = driver.find_elements_by_xpath("//span[@class='price-format__large-symbols']/following-sibling::span")
            try:
                price = float(price[0].text + "." + price[1].text)
            except:
                logging.info('Price not found, skipping url')
                price = None

        else:
            raise ValueError('Other sites have not been implemented yet.')

        # append info to dataframe
        output_df = output_df.append({'Description': site_df['description'].iloc[i],
                                      'Date': date_pulled,
                                      'Price': price},
                                     ignore_index=True)

    # save info to csv
    logging.info(f'Saving prices to {output_file}')
    output_df.to_csv(output_file, index=None)


if __name__ == '__main__':
    cli(obj={})
