Source:
----
* [頂好](https://sbd-ec.wellcome.com.tw)
* [愛買](http://www.gohappy.com.tw/shopping/Browse.do?op=vc&cid=31581&sid=12)
* [大潤發](http://www.rt-mart.com.tw/fresh/)
* [楓康](http://shop.supermarket.com.tw/)
* [HonestBee](https://www.honestbee.tw/)

Configs
-----
* Chilled Chicken (Taiwan)
* Chilled Pork (Taiwan)
* Fruits
* Vegetables
* Grains

Data
-----
|    | 分類  | 市場名 | 品名               | 單價 | 重量(克) | 每公斤價格 | 來源                             | 
|----|-----|-----|------------------|----|-------|-------|--------------------------------| 
| 0  | 紅蘿蔔 | 大潤發 | 台灣紅蘿蔔(格外品)-      | 39 | 1000  | 39.0  | http://www.rt-mart.com.tw      | 
| 1  | 紅蘿蔔 | 大潤發 | (B)台灣紅蘿蔔(產銷履歷)   | 27 | 600   | 45.0  | http://www.rt-mart.com.tw      | 
| 2  | 紅蘿蔔 | 大潤發 | (B)綠天使紅蘿蔔(產銷履歷)  | 27 | 600   | 45.0  | http://www.rt-mart.com.tw      | 
| 3  | 紅蘿蔔 | 大潤發 | 台灣紅蘿蔔            | 29 | 600   | 48.33 | http://www.rt-mart.com.tw      | 
| 4  | 紅蘿蔔 | 大潤發 | 台灣紅蘿蔔            | 32 | 600   | 53.33 | http://www.rt-mart.com.tw      | 
| 5  | 紅蘿蔔 | 家樂福 | 履歷紅蘿蔔            | 54 | 1000  | 54.0  | https://www.honestbee.tw/zh-TW | 
| 6  | 紅蘿蔔 | 大潤發 | 臺灣紅蘿蔔(產銷履歷)      | 34 | 600   | 56.67 | https://www.honestbee.tw/zh-TW | 
| 7  | 紅蘿蔔 | 大潤發 | 臺灣紅蘿蔔            | 34 | 600   | 56.67 | https://www.honestbee.tw/zh-TW | 
| 8  | 紅蘿蔔 | 大潤發 | 臺灣紅蘿蔔            | 34 | 600   | 56.67 | https://www.honestbee.tw/zh-TW | 
| 9  | 紅蘿蔔 | 愛買  | 產銷履歷紅蘿蔔          | 69 | 1200  | 57.5  | http://www.gohappy.com.tw      | 
| 10 | 紅蘿蔔 | 愛買  | 產銷履歷紅蘿蔔          | 35 | 600   | 58.33 | http://www.gohappy.com.tw      | 
| 11 | 紅蘿蔔 | 大潤發 | 台灣紅蘿蔔            | 12 | 200   | 60.0  | http://www.rt-mart.com.tw      | 
| 12 | 紅蘿蔔 | 頂好  | 雲林斗南紅蘿蔔          | 35 | 550   | 63.64 | https://sbd-ec.wellcome.com.tw | 
| 13 | 紅蘿蔔 | 濱江  | 紅蘿蔔-M            | 24 | 360   | 66.67 | https://www.honestbee.tw/zh-TW | 
| 14 | 紅蘿蔔 | 頂好  | 履歷紅蘿蔔            | 69 | 1000  | 69.0  | https://sbd-ec.wellcome.com.tw | 
| 15 | 紅蘿蔔 | 濱江  | 紅蘿蔔              | 13 | 180   | 72.22 | https://www.honestbee.tw/zh-TW | 
| 16 | 紅蘿蔔 | 大潤發 | 臺灣紅蘿蔔            | 18 | 200   | 90.0  | https://www.honestbee.tw/zh-TW | 

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


