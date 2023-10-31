import scrapy
import json
from scrapy.selector import Selector

class SellingsSpider(scrapy.Spider):
    name = "sellings"
    allowed_domains = ["store.steampowered.com"]
    start=0
    def start_requests(self):
        yield scrapy.Request(
            url = f"https://store.steampowered.com/search/results/?query&start={self.start}&count=50&dynamic_data=&sort_by=_ASC&supportedlang=english&snr=1_7_7_7000_7&filter=topsellers&infinite=1",
            method="GET",
            headers={
                'Content-Type': 'application/json'
            },
            callback=self.parse
        )


    def parse(self, response):
        resp_dict = json.loads(response.body)
        html = resp_dict.get("results_html")
        sel = Selector(text = html)
        games = sel.xpath("//body/a")

        for game in games:
            link = game.xpath("@href").get()
            name = game.xpath("div[@class='responsive_search_name_combined']/div[@class='col search_name ellipsis']/span/text()").get()
            date = game.xpath("div[@class='responsive_search_name_combined']/div[@class='col search_released responsive_secondrow']/text()").get()
            actual_price = game.xpath("div[@class='responsive_search_name_combined']//div[@class='discount_original_price']/text()").get()
            discounted_price = game.xpath("div[@class='responsive_search_name_combined']//div[@class='discount_final_price']/text()").get()

            yield scrapy.Request(
                url = link,
                callback = self.update_parse,
                meta={
                    "link":link,
                    "name":name,
                    "dt":date,
                    "ap":actual_price,
                    "dp":discounted_price  
                }
            )
        if self.start != 200:
            self.start += 50
            yield scrapy.Request(
                url = f"https://store.steampowered.com/search/results/?query&start={self.start}&count=50&dynamic_data=&sort_by=_ASC&supportedlang=english&snr=1_7_7_7000_7&filter=topsellers&infinite=1",
                method="GET",
                headers={
                    'Content-Type': 'application/json'
                },
                callback=self.parse
            )

    def update_parse(self,response):
        recent_reviews_resp = response.xpath("//div[@class='summary column']/span[contains(@class,'game_review_summary')]/text()").get()
        recent_reviews_num = response.xpath("//div[@class='summary column']/span[@class='responsive_hidden']/text()").get()

        if recent_reviews_num:
            recent_reviews_num_normalised = recent_reviews_num.replace('\r','').replace('\n','').replace('(','').replace(')','').replace('\t','')

        developer = response.xpath("//div[@id='developers_list']/a/text()").get()

        link = response.request.meta['link']
        name = response.request.meta['name']
        date = response.request.meta['dt']
        actual_price = response.request.meta['ap']
        discounted_price = response.request.meta['dp']

        yield{
            "link":link,
            "name":name,
            "date":date,
            "actual_price":actual_price,
            "discounted_price":discounted_price,
            "recent_reviews":recent_reviews_resp,
            "recent_reviews_num":recent_reviews_num_normalised,
            "developer":developer
        }



        
      
       