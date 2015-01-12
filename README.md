accountability_tracker
======================

SCPR repository to house an iterative Django project that will store and provide data for a series of projects dealing with accountability in the political process.

Table of Contents
=================

* [Wiki](https://github.com/SCPR/accountability-tracker/wiki)
* [Maplight Finance](#maplight_finance)
* [Ballot Measure/Initiative Tracker](#ballot_initiatives)

----

[maplight_finance](/maplight_finance)
==================

Using the MapLight API, this application retrieves contributions to the six approved statewide measures that appear on the November 2014 ballot and builds charts with the data using [django-bakery](https://github.com/datadesk/django-bakery).

* [Documentation](/maplight_finance)
* Pubished content
    * [Prop 1 — the state's big water bond](http://www.scpr.org/news/2014/10/17/47388/election-2014-faq-prop-1-the-state-s-big-water-bon/#finance)
    * [Prop 2 — state budget and rainy day fund](http://www.scpr.org/news/2014/10/17/47410/election-2014-faq-prop-2-state-budget-and-rainy-da/#finance)
    * [Prop 45 — health insurance rate changes](http://www.scpr.org/news/2014/10/17/47468/election-2014-faq-prop-45-health-insurance-rate-ch/#finance)
    * [Prop 46 — doctor drug testing and medical negligence](http://www.scpr.org/news/2014/10/17/47321/election-2014-faq-prop-46-doctor-drug-testing-and/#finance)
    * [Prop 47 — criminal sentencing](http://www.scpr.org/news/2014/10/17/47466/election-2014-faq-prop-47-criminal-sentencing/#finance)
    * [Prop 48 — Indian gaming compacts](http://www.scpr.org/news/2014/10/21/47520/election-2014-faq-prop-48-indian-gaming-compacts/#finance)

ballot_initiatives
==================

* A semi-automated interactive tracker based on information from the Secretary of State and Attorney General.

**The basics**:

* Initiative title
* Summary
* LAO's fiscal impact statement
* Link to full text

**Could also include**:

* Deeper research, such as campaign finance
* Who's backing it/opposing it even before it's qualified for the ballot (MapLight's not even doing this)

**Engagement and interactivity**:

* ability to share individual initiatives with friends
* ability to "vote" up or down, a la Facebook's "Like" button
  * this gives us a rough gauge of popular sentiment...the more widely it's shared and used, the more accurate these numbers will reflect the views of our audience and possibly beyond
  * ability to comment/discuss, with comment threads attached to each initiative

**Public service**:

* potentially taking this a step further, some way to link the audience to the proponents if they want to sign
* you might not run into a signature gatherer, and if you do, it's probably a grocery store and you don't want to be bothered at that moment...allowing people to get involved on their own time is a useful public service

* Digital Explainers
    * web-based articles examining specific initiatives, but also explainers about the process.
        * how much does it cost to get 504,000 signatures, that is, to get an initiative on the ballot?
        * who writes our initiatives? It's actually an exclusive club of lawyers in California
        * what does it take to find 504,000 VALID signatures...one measure shows tens of thousands of invalid signatures...is that common? Are there alternatives to the grocery-store signature-gathering process?

* Radio spots
    * Two-ways or features promoting the tracker, explaining the initiative process in more detail, and examining specific measures
        * Off-season, these would be about initiatives that are in circulation, gathering signatures, making people more aware of what grassroots changes are afoot and what could appear on future ballots
        * On-season, these would focus more on qualified ballot measures to prepare for upcoming elections

* Tie-ins to our political coverage
    * Relevant stories can always link back to the tracker, and the tracker can curate relevant stories from our staff, including blog posts from Represent!

**Further Notes**:

* Could be billed as part of our stalled Project Citizen initiative, which could be rekindled and have a higher profile on the politics vertical?

* We did a version of this at [KCET](http://www.kcet.org/news/ballotbrief/ballot-measures/california-propositions-guide-2012-cheat-sheet.html) and it was the single-most successful digital campaign the site had ever run. This proposal would be an improvement on what we did there, taking it to another level.