# pyractice

## wp2hexo
Generate simplest blog posts from Wordpress export xml to Hexo (Markdown) files

### Requirement
1. Built on Python 3.6.3
2. Generated folder structure are base on Hexo 3.3.9
3. Wordpress exported xml files are tested from Wordpress 4.8.2 and old version in 2013 - the year I stopped blogging with Wordpress
4. It uses another python tool [html2text](https://github.com/aaronsw/html2text) to convert main HTML content to Markdown: ```pip install html2text```

### Usage
```wp2hexo.py <wordpress_exported.xml> [hexo_blog_folder]```
1. If [hexo_blog_folder] is not specified, 'hexo' will be created as top level of hexo blog in current directory.

2. Output will be like this:
```
  /[hexo_blog_folder]  
  /[hexo_blog_folder]/source  
  /[hexo_blog_folder]/source/_drafts/...md  
  /[hexo_blog_folder]/source/_posts/...md  
  /[hexo_blog_folder]/source/[Page]/index.md  
  /[hexo_blog_folder]/[Blog].md
```

3. Copy source folder to your real hexo blog folder if needed then run hexo.

  There would still be some posts those can't process well, then manually modify will be OK.



## fapiao.py

Due to limited fapiao acquisition, I need to get the most use of current ones. It's a small script for it.

Usage:
```fapiao.py <total_amount> <fapiao_amount_1>,...,<fapiao_amount_n>```

Then it will get the fapiao selecting choices. Ex.:  
```
fapiao.py 200 50,60,70,80,100 <Enter>
--------------------------------------------------
The best choices of fapiao are: (50.0, 60.0, 100.0).

All options are:

(summary, (combinations))

(210.0, (50.0, 60.0, 100.0))
(210.0, (60.0, 70.0, 80.0))
(220.0, (50.0, 70.0, 100.0))
(230.0, (50.0, 80.0, 100.0))
(230.0, (60.0, 70.0, 100.0))
(240.0, (60.0, 80.0, 100.0))
(250.0, (70.0, 80.0, 100.0))
(260.0, (50.0, 60.0, 70.0, 80.0))
(280.0, (50.0, 60.0, 70.0, 100.0))
(290.0, (50.0, 60.0, 80.0, 100.0))
(300.0, (50.0, 70.0, 80.0, 100.0))
(310.0, (60.0, 70.0, 80.0, 100.0))
(360.0, (50.0, 60.0, 70.0, 80.0, 100.0))
--------------------------------------------------
```
