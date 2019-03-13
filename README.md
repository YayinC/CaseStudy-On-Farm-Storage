# Case Study: On-farm Storage Capacity Analysis
## 0. Notes
There are several items in this repo:<br>
(1) Case Study.html, HTML file exported through Jupyter Notebook, the code for data preparation and spatial analysis<br>
View it here: http://htmlpreview.github.io/?https://github.com/YayinC/casestudy-on-farm-storage/blob/master/Case%20Study.html
<br>
(2) script.js, JavaScript file, the code for data visualization<br>
(3) index.html, HTML file, the code for data visualization<br>
(4) Reset.css & style.css, css file, the code for data visualization <br><br>

## 1. Data Cleaning and Wrangling
Before conducting the spatial analysis, we should clean the data and do some data wrangling. We have several steps:<br>
(1) First, we want to remove the buildings that are located on the municipal parcels, because they are not grain bins. 
We can check whether a parcel is municipal based on two criteria: <br>
a. If a parcel is a municipal parcel, the parcel owner name doesn't include "LLC", "LTD", "INC", "CO" or "CORP", and<br>
b. If a parcel owner name includes "STATE", "CITY", "COUNTY" or "DEPT", the parcel should be a municipal parcel<br>
Then we can create a new column indicating whether it is a municipal parcel (0/1). <br>
Next, we can spatial join the "parcels" geodataframe to the "buildings" geodataframe. By doing so, every building will be joined to all parcels
if the building footprint intersects with the parcel. Considering that one building footprint may intersect with more than one parcel (actually this case is very rare), we can group by building id, and summarize by the "maximum" value of the municipal field ("muni"). If a building footprint intersects with at least one municipal parcel, the building will be seen as "municipal building". After this step, we can remove all municipal building. <br>
Although in this analysis, there is no municipal building in the geodataframe, we can replicate the analysis to other datasets as well.<br>
(2) Second, we can calculate the bottom area of the grain bins (sqft) based on the diameter. <br>
(3) Third, we only care about agricultural parcels. To select out agricultural parcels, we can filter by "FARM_AREA" (the farmland area of the parcel). We can select out all parcels whose farmland area is more than zero. These parcels are regarded as agricultural parcels. <br>
<br><br>


## 2. Spatial Analysis
Now, we have two datasets after data wrangling. One dataset contains all grain bins, and the other one contains all agricultural parcels. In this part, we have several steps:<br>
(1) First, we can dissolve the agricultural parcels by owner name, since one farm may contain more than one parcel. <br>
(2) Second, we want to separate all multipolygons. If two polygons are not adjacent to each other, we want to separate them into two single polygons even though they have the same owner.<br>
(3) Third, we spatial join the dissolved polygons (already exploded in the above step) with the grain bins. Then, we can group by the polygon id, and summarize by the sum of the bottom areas. In this step, 
we are able to know the sum of the bottom areas of all grain bins which intersect with the polygons. <br>
(4) Next, we can calculate the minimum total volume and the maximum total volume of the grain bins for each polygon, based on the minimum height (15 feet), and maximum height (54 feet). <br>
The formula is: volume = bottom area * height.<br>
<5> Last, we want to estimate the capacity based on the volume. Based on the experience, we can roughly estimate:<br>
bushels = volume * 0.85<br>
Now, we have the total minimum volume/capacity and maximum volume/capacity of the grain bins for each polygon.<br><br>

## 3. Data Visualization
Through the above analysis, we get the estimated range of the volume/capacity of the grain bins for each polygon 
(only considering the agricultural polygons which intersect with the footprint of the grain bins)<br>
We can map the analysis using Mapbox GL. On this map, as we move the mouse, the owner name and the estimated range of storage capacity will show on the sidebar. Also, we can click the grain bins and see the radius and the area of the grain bins. 
