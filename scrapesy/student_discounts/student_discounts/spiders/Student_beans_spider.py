import scrapy

class StudentBeansSpider(scrapy.Spider):
    name = 'student_beans_spider'
    start_urls = ['https://www.studentbeans.com/us/trending-discounts?_accounts_session=c471d4ec43b39deb2f62213d5554cca3--98710f0d3f49e8058bfc2bcb88051d92a021d542fb3c7f5a7033fa4dda872355']

    def parse(self, response):
        discounts = len(response.xpath('//article/a[1]/div[2]/div[2]/h4/text()').get())
        for i in range(discounts) :
            x=i+1
            yield {
            'title': response.xpath('//*[@id="__next"]/div/main/div/div/div/div/section/div/div['+str(x)+']/article/a[2]/text()').get(),
            'description': response.xpath('//*[@id="__next"]/div/main/div/div/div/div/section/div/div['+str(x)+']/article/a[1]/div[2]/div[2]/h4/text()').get(),
            }
