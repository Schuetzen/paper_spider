# Notion_bot-文献信息爬虫

# V1.0

## 需求
   1. 实现特定文献的检索功能
   2. 截取文献的被引量，doi，作者，单位
   3. notion机器人写入数据库中

## 思路
* 'extract_page()' 传入网页url,提取文章信息
* 'search_paper()' 通过文章名称检索url,成功检索返回url，失败返回NA

