import scrapy


class PaperCardSpider(scrapy.Spider):
    name = 'paper_card'
    allowed_domains = ['www.americangreetings.com']
    start_urls = [
        'http://www.americangreetings.com//cards/paper-cards/greeting-cards/_/N-haomya']

    def parse(self, response):
        topic = response.xpath(
            '//h2[@class="refinement-dimension-header-text"]//text()').getall()
        filters = response.xpath('//ul[@class="refinement-dimension-text"]')
        for filter in range(len(filters)):
            category = filters[filter].xpath(
                './/li[@class="refinement-dimension-list-item"]')
            for item in category:
                item_name = item.xpath('./a/text()').get()
                item_location = item.xpath('./a/@href').get()
                yield response.follow(item_location, callback=self.parse_cardlocation, meta={'topic': topic[filter], 'item_name': item_name})

    def parse_cardlocation(self, response):
        card_details = response.xpath(
            '//li[@class="product-item results-list-product product-type-hardgoodProduct col-lg-4 col-md-4 col-sm-4 col-xs-4 col-xxs-6 three-across"]//a//@href')
        for card_detail in card_details:
            yield response.follow(card_detail, callback=self.parse_carddetail, meta={'topic': response.meta.get('topic', ''), 'item_name': response.meta.get('item_name', ''), 'id2': response.url})

        next_page = response.xpath(
            '//a[@class="pagination-next-link"]/@href').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse_cardlocation, meta={'topic': response.meta.get('topic', ''), 'item_name': response.meta.get('item_name', ''), 'id2': response.url})

    def cleanup_list(self, list_of_items):
        cleaned_list = [word.strip()for word in list_of_items]
        if "" in cleaned_list:
            cleaned_list.remove("")
        if "Item" in cleaned_list:
            cleaned_list.remove("Item")
        return cleaned_list

    def parse_carddetail(self, response):
        name = response.xpath(
            '//div[@class="inner-container col-sm-6  "]/h1/text()').get().strip()
        rate = response.xpath(
            '//div[@class="product-price-display col-lg-12"]/span/text()').get().strip()
        image = response.xpath(
            '//div[@class="thumbs-container col-lg-12 hidden-xs"]//img/@src').getall()
        get_front_content = response.xpath(
            '//div[@class="product-front-verse"]/text()').getall()
        front_content = self.cleanup_list(get_front_content)
        get_inside_content = response.xpath(
            '//div[@class="product-inside-verse"]/text()').getall()
        inside_content = self.cleanup_list(get_inside_content)
        product_content = {}
        get_product_content = response.xpath(
            '//div[@class="product-display-long-description col-lg-12"]/p/text()').getall()
        cleaned_product_content = self.cleanup_list(get_product_content)
        get_product_points = response.xpath(
            '//div[@class="product-display-long-description col-lg-12"]//ul//li/text()').getall()
        product_content['content']=cleaned_product_content
        product_content['points']=get_product_points 
        if product_content['content'] == []:
            print ("True")
            get_product_content = response.xpath(
            '//div[@class="product-display-long-description col-lg-12"]/text()').getall()
            cleaned_product_content = self.cleanup_list(get_product_content)
            product_content['content']=cleaned_product_content
        get_item_content = response.xpath(
            '//div[@class="cartridge-spacing col-lg-12"]//text()').getall()
        item_content = self.cleanup_list(get_item_content)
        yield {
            'id': response.url,
            'id2': response.meta.get('id2', ''),
            response.meta.get('topic', ''): response.meta.get('item_name', ''),
            'name': name,
            'rate': rate,
            'image': image,
            'front': front_content,
            'inside': inside_content,
            'product': product_content,
            'item': item_content
        }
