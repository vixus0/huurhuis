pararius:
	@scrapy runspider spiders/pararius.py -o pararius.json
	@jq -r '.[] | select(.description|test("([34]|three|four) (werkende|working|people|person|persons|personen|share|sharing|tenants|delers)")) | .url' < pararius.json | sort -u

funda:
	firefox 'https://www.startpage.com/do/metasearch.pl?query=site:funda.nl/huur -verhuurd "Amsterdam" "3 werkende|working|people|person|persons|personen|share|sharing|tenants"' 'https://www.startpage.com/do/metasearch.pl?query=site:funda.nl/huur -verhuurd "Amsterdam" "4 werkende|working|people|person|persons|personen|share|sharing|tenants"'
