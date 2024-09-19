import scrapy

class UnidaysScraperSpider(scrapy.Spider):
    name = 'Unidays_spider'
    start_urls = ['https://www.myunidays.com/US/en-US/list/all/AtoZ']
    # //*[@id="Page_List_all_AtoZ"]/div[4]/article[2]/a/div[2]/div/picture/img
    # //*[@id="Page_List_all_AtoZ"]/div[4]/article[2]/a/div[2]/div/picture/img
    # //*[@id="Page_List_all_AtoZ"]/div[4]/article[6]/a/div[2]/div/picture/img
    
    def parse(self, response):
        # yield {
        # 'title': len(response.xpath('//*[@id="Page_List_all_AtoZ"]/div[4]/article').get()),
        # 'description': response.xpath('//*[@id="Page_List_all_AtoZ"]/div[4]/article[1]/a/div[2]/p[2]/text()').get(),
        # }
        discounts = len(response.xpath('//*[@id="Page_List_all_AtoZ"]/div[4]/article').get())
        for i in range(discounts) :
            x=i+1
            yield {
            'title': response.xpath('//*[@id="Page_List_all_AtoZ"]/div[4]/article['+str(x)+']/a/div[2]/div/picture/img/@alt').get(),
            'description': response.xpath('//*[@id="Page_List_all_AtoZ"]/div[4]/article['+str(x)+']/a/div[2]/p[2]/text()').get(),
            }

