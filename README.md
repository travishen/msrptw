Source:
----
* [頂好](https://sbd-ec.wellcome.com.tw)
* [愛買](http://www.gohappy.com.tw/shopping/Browse.do?op=vc&cid=31581&sid=12)
* [大潤發](http://www.rt-mart.com.tw/fresh/)
* [楓康](http://shop.supermarket.com.tw/)
* [HonestBee](https://www.honestbee.tw/)

Usage
-----
Collect internet marketing retail price from Taiwan supermarkets

Setup database(e.g. postgresql):

    $ python -m msrptw.builder --dbpath postgresql+psycopg2://username:password@host/dbname --setup

Build daily data:

    $ python -m msrptw.builder --dbpath postgresql+psycopg2://username:password@host/dbname

Classification
-----
Automatically

    2017-11-21 20:41:49,302 INFO  [msrptw.marketbrowser][MainThread] 將商品澳洲綠豆自動定義為綠豆
    2017-11-21 20:41:49,317 INFO  [msrptw.marketbrowser][MainThread] 將商品屏東紅豆自動定義為紅豆

Manually

    無法自動分類商品「活菌豬松阪肉」，產地臺灣，請定義產品類型或放棄(Enter)
    (0): 豬腹脇肉 (1): 豬肩胛肉 (2): 豬肩頸肉 (3): 豬小排 (4): 豬里肌肉 (5): 豬腿肉 (6): 豬絞肉 (7): 豬肉片 (8): 豬肉絲 (9): 豬軟骨 (10): 豬肋骨 (11): 豬排骨 :2
    2017-11-21 20:46:29,653 INFO  [msrptw.marketbrowser][MainThread] 將商品活菌豬松阪肉人工定義為豬肩頸肉


