# AMZN-Tracking-Web-ap

Goal of the current version of this app is to do 2 things: 

- Create a "Combined Table" which would be based off of the AMZN order report but this "combined table" would include a column with tracking numbers( as of right now, the tracking file would be manually supplied to the website by the end user interacting with the website ) end user would drag and drop or upload AMZN order reports and a matching Tracking report (left join tracking to Order report) (note: it is, in fact possible, to have 2 or more tracking numbers for the same recipient, keep this in mind) 

- Make an api request to UPS and / or USPS to track packages for either carrier. this api request would take the tracking numbers from the "combined table", and make a request to check the current tracking status. the current status of the tracking number would then be placed within another column in the "Combined table" the final version of the "combined table" is what would be used to track shipment status of orders sent out. aside from order tracking, there are some additional requests that the "Combined table" could help accomplish:

- from the "combined table"( "CT" from this point fwd) it would be great to know the exact box count(we hold multiple different sized boxes for diffferent products) needed for the amount / type of orders to be shipped out (we can link box sizes to product sku or ASIN, one of many product identifiers on the AMZN Order report TSV file
