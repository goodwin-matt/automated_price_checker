import requests
from bs4 import BeautifulSoup
import click
import pandas as pd
from datetime import datetime


@click.group()
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)
    ctx.obj['HEADERS'] = ({'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})


@cli.command()
@click.option('--site-file', default=None, required=True)
@click.option('--output-file', default=None, required=True)
@click.pass_context
def price_parser(ctx, site_file, output_file):
    """
    Parse prices for different urls
    """

    # read in list of websites to look up
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
        # request url content
        page = requests.get(site_df['url'].iloc[i], headers=ctx.obj['HEADERS'])
        # parse html
        soup = BeautifulSoup(page.content, 'html.parser')

        # get price depending on site
        if site_df['site'].iloc[i].lower() == 'amazon':
            price = soup.find(id='priceblock_ourprice').get_text()
        else:
            raise ValueError('Other sites have not been implemented yet.')

        # append info to dataframe
        output_df = output_df.append({'Description': site_df['description'].iloc[i],
                                      'Date': date_pulled,
                                      'Price': price},
                                     ignore_index=True)

    # save info to csv
    output_df.to_csv(output_file, index=None)


if __name__ == '__main__':
    cli(obj={})
