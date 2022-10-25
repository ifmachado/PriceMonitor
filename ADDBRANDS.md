ADDING NEW BRANDS:

1. Inspect website for price and image elements. 
2. Add to brands specs dict:
	-	price element’s class and tag type. 	-	 class of the closest div to the img tag (make sure it’s unique!). 
3. Add brand name to conditionals on fetch_name_brand function. 
4. Test functions as they are. Potential problems:
	⁃	Some brands have a specific way of declaring img tags or img src attributte (ie: data-src instead of src). Add conditional in fetch_image function.

	⁃	Some brands will have specific tags for reduced and non reduced prices. In brand specs dict, add all appropriate tag types and class and in the fetch_price function add the conditionals to match that.

	⁃	Some brands have a specific way of formatting how prices are displayed (ie. Trailing zeros, etc). Adjust as necessary on fetch_price function before returning the prices. 
5. Save brand logo image to checker/static/checker/images.

6. Adjust index.html to include the brand logo img and link redirect in the header block.
