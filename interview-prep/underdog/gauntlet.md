# Underdog Interview Notes


## Greg Roseberry - SVP, Finance

About me
* Started my career in Supply Chain
* Early career opportunity at Chewy to start using analytics
* From there, experienced different industries: Manufacturing, eCommerce, Quick Service Restaurant, Salon, Public Safety
* 3.5 years heavy experience in dbt modeling, dashboard building, ad hoc analytics serving Operations, Product, Engineering, CSS, others

Type of Analytics professional I am...
1. Naturally curious -- intentionally explored different industries, functional teams
   1. Conversation agent via andorid app for NFL stats
      1. Practicing concepts like efficient agent orchestration -- get it to answer the question not just correctly, but quickly and at a lower token cost
2. Motivated by problem-solving -> not seeking credit
   1. Go find things to work on, don't wait. Solve as many problems as I can.
3. Eager to be a good partner
   1. Available, good communicator, be reliable, not standoffish


Important in next job
* Fast, collaborative, lean environment, not too siloed
* Using cutting edge technology: AI for conversational analytics
* Best In Class Analytics Attitude: put business metrics/definitions in code, automate things, avoid manual calculations




Projects where I solved a problem outside of my lane:
* DYGWYB
* Pipeline Churn dashboard
* Subway Bottle Rebates
* Subway Tableau Dashboard Suite







Questions for Greg:
* I've heard great things about the conversational analytics but how close or far would you say it is to a complete experience for you?
  * In terms of latency, accuracy, having all the right data/metrics, etc.
    * Answer: Training?
* What formalized recurring reporting along the lines of a WBR, QBR, Board Deck, etc. is important for the company, and has AI changed how that is being delivered?
* Are there specific areas where you think Analytics Engineering could be partnering more effectively, or branching off into new initiatives, with other departments?
* What growing pains stand out amidst all the change of entering prediction markets and then operating your own exchange?
  * Answer: Hard to pivot on the fly, not exactly the right shape of org, done a good job of managing the business model change, financial discipline came late,



















## Nick Holt — Sr. Manager, Commercial Analytics 10:15

**Focus:** Marketing, Promo, CRM
**Tenure:** UD for 3 years
<br> Core Value: **Act With Urgency**

### Focus

> Wants to make sure I can be a good partner to any stakeholder, particularly his analysts
<br> Can you prioritize, engage, translate business questions into data modeling strategies?
<br> Looking for someone who will work as an extension of the Analytics team, to understand their needs and build accordingly.
<br> Understand the problem → unblock the team → roll out a data model / Hex solution / whatever
<br> Looking for someone who will work as an extension of the Analytics team, to understand their needs and build accordingly.
<br> Data Analyst builds out a dashboard if needed.

My approach to prioritization:
* Always have a visible and broadcasted priority queue (JIRA board, Slack comms, whatever works)
* As much as possible seek to have established timeline estimates (more specific for top of queue, vague is ok for bottom of queue)
* Seek to understand (through conversation and data exploration) before adding items to the queue: if helpful utilize things like RFC, Wireframes

My approach to collaboration:
* Understand what support team has been getting and where they want additional support vs maintaining status quo
  * Prefer to have scheduled meeting cadences (roadmap review basically)
  * Happy to attend as many business meetings as makes sense
* Be available, reachable, responsible, reliable
* Be communicative w/o being annoying
* Provide templates (RFC, Wireframe) as much as is useful. Never too rigid.
* Provide iterative updates frequently, both to show proof of progress and give opportunity for feedback loops along the way
  * Prioritize unblocking folks whenever possible

### Example Questions

> How do you decide which data models or metrics to prioritize when you can't do everything?

1. When collecting epics/tickets establish "when do you need this by?"
   1. Collect info about urgency, cost of not having it
2. Have a broadcast work queue, ordered, with ETAs.
3. Invite feedback to re-order items based on priority: ideally coming from a department lead or assigned stand-in.
4. Seperately: strive to handle quick wins outside of primary queue if possible w/o missing other timelines.
5. Ultimately I am comfortable making judgment calls on the best order in which to do things; start there and allow others to advise on + or - to item priority

> Tell me about a time when your decision on a data layer enabled a primary business decision. <br>

Example: sim_lte_usage_costs_performance_daily
* Combined sim consumption data, carrier-plan billing schedules, device data
* Dataset at the device-daily grain, enabling reporting around "sim carrier costs"
  * Persistent data problems, set up targeted dbt tests to warn if (for example) Verizon sims reporting >0 usage with zero cost, or 0 usage after ~3 days despite being live in the field, no record created in source ingestion (pipeline issue)
* Worked w/ a stakeholder to develop a sigma dashboard surfacing insights...
  * "Top N Sims by Carrier/Usage"
  * Explore/drill-down functionality to examine dynamic carrier switching
* PM stated "$240k/month saving" based on improved carrier selection

### Notes From Conversation

>

---

## James Kim — Staff Analytics Engineer 11:00

**Background:** Came over as a Data Engineer into this role.
**Profile:** Very technically sound. More of a backend/technical guy than working with business-facing people. Probably a Grayson type.
<br>Core Value: **Give A Shit**

### Focus

* dbt
* Infrastructure
* Modeling
* Someone who will make our team better as a data owner.
* Will write some SQL.
* Syntax should be variable (Postgres, Snowflake).

### Example Questions

> How do you structure dbt projects for readability and testing at scale?
* High level:
  * base/cdc layer transforms nothing except to explicit type cast from the payload
  * staging layer: dbt generic tests (unique, non-null), de-duping
  * intermediate (core extensions): light renaming, can add derived dimensions, some joins but don't change the grain of the core table (e.g. Locations can join to Opportunities but not Work Orders)
  * marts: business domains and broadly reusable concepts e.g. device_health_check_events. Some joins and grain change acceptable. a Building block into more complicated models. Can rename system labels to business terminolody
  * analytics: final layer, can be very bespoke based on intention (e.g. Reschedule Performance)
* Testing: generic (unique, non-null, accepted values) primarily in the staging layer for validating source system data. Continue to have unique checks on whatever ID at downstream layer when joins introduce possibility for grain change. Further build more niche tests at the gold layer as needed (e.g. checking renewal values for negative dollars)
* Other stuff:
  * enforce common naming conventions across the repo (opportunityid, salesforce_opportunity_id)
  * owner tagging
  *

> Merge or Insert:
* Merge: for late-arriving records, updates to records where capturing change (at id level) is not needed
  * device_health_performance_hourly
* append (or insert): faster/cheaper for append-only


> What's a major data model you've built that required multiple business user input and was highly complex?
* Example: device_health_performance_daily
* Established list of critical dimensions from business users (across systems gimlet, hpnotiq, salesforce)
* Complexity came from needing to map device-metric reads to the hourly spine, apply 24hr smoothing, rebuild rows in case of late-arriving records w/o breaking the smoothing or causing row duplication. is ~80M records per day so don't want to have to rebuild.
* Set up incremental merge strategy that uses a 72hr lookback insert (with 96hr lookback context) to post-fact correct rows created which were missing late-arriving data. Runs 3x/day because the business needs intra-day updates.
  * Bonus: built in some "backfill_enabled" jinja rules to allow for incrementally loading in history (e.g. one month at a time) to batch backfill at business request
* Did some testing w/ Snowflake account_usage to check different cluster id strategies (winner was calendar_date_hour, metric). I checked:
  * bytes_scanned
  * partitions_scanned
  * partitions_total
  * elapsed seconds


> How do you decide what logic belongs in dbt vs. downstream BI tools?
* Heavy biased towards important governed metrics, derived dimensions, etc. should live in the repo.
  * Counter-example: at Flock different people defining a "Live" site in sigma or ad hoc sql.
* In downstream BI tools: I think it's fair for an analyst to do what they need to do to support an analysis or a dashboard, but as a company we should strive to have any metric that could rise to the importance of a QBR/OKR/Board metric, it lives in the repo.
  * Can reference chat logs to understand opportunities to clarify any metric drift.
* Bottom-line: presentation-specific logic can go in a BI tool but avoid putting any reusable business definitions there.

> And semantic layer vs. YAML?
* Lightdash may compile semantic definitions written in model YAML. Snowflake may house them in semantic views.
* Snowflake semantic view holds tables, relationships, facts (how much, how many), dimensions (who, what), metrics, sql blocks...
* I am using metrics directly in model yml's for postgres-dbt-lightdash

### Notes From Conversation

>

---

## About Me
* Degrees in SCM and Marketing.
* Career started in Supply Chain as a Purchaser and then Supply Planner. Got the opportunity to pull my own data using SQL at Chewy, recognized this as a needed and high-leverage skill, and the rest is history
* Intentionally sought out a variety of industries (eCommerce, manufacturing, restuarant, salon, public safety) and support roles (merchandising, logistics, operations, Customer Success, product, engineering, some finance/revenue)
* Been doing dedicated AE at Flock for 3.5 years. Good: deep comfort working in dbt, getting tangential familiarility with ingestion pipelines, learning more about optimizing models. Not working as much with business users as I'd prefer. Not very AI-forward.
* PERSONAL:
  * Growing interest in better understanding all the emerging technology: different types of databases, best ways to optimize build/query/storage costs, and especially AI (topics like best repo structure for feeding context to agents without bloat and of course getting the right answers reliably, Skills, Evals, self-improving feedback loops)
    * NFL agent app project
  * Next I want to work in a role where I can continue to work closely w/ business users and play a big role in problem solving, with an AE focus on modeling and conversational analytics as opposed to ad hoc analysis or dashboard building
  * Been a heavy Underdog user for about 3 years

## Eamon Glackin — Sr. Director of Analytics 12:00

**Reports into:** Greg Rosebury, SVP of Finance
**Context:** This is his org.
Core Values: **Be Ambitious, Be Optimistic**

### Focus Areas

* Be as scrappy as possible.
* How do you continuously look to improve the system? Challenge it, etc.
* If you find something broken, go fix it.

### Example Questions

> How have you used AI to improve your personal workloads and the workloads of teams you support?

* For me
  * Code development multiplier via IDE agent for basically automating dbt model build for new source ingestion, or propogating YML metadata throughout the repo
  * CortexCode to assist in difficult investigations (tanqueray example)
  * CortexCode to assist in validation testing in sql terminal
  * CI/CD
  * I'm doing all the things I used to do, just faster
  * I'm also tinkering with AI tools in my personal time, building an Android app / chatbot to answer football questions etc.

* For others
  * It's tough at Flock. Want desperately to get Product Analysts into dbt, or at least using Cursor or Snowflake.
  * There was the streamlit app for redshift -> snowflake sql conversion
  * Have this idea to automate the Product Data Questions channel with a chatbot

> Tell me about a time you identified a problem and ran to a solution without waiting on someone. What was the result? What was the impact?
* Three examples
  * Subway Restaurant bottle rebates
    * Simple audit saved money, close to $1M (at least 800k)
  * Jameson ingestion pipeline alerting
    * Set up a custom dbt test that checks for distance between created_at and loaded_at and fires off a Warn alert if any records >= 6hrs (or something like that)
  * Pipeline Slip dashboard for Weekly Top 15

Team
+
-
Leaders to work with and for
+
-

### Notes From Conversation

> Going: feel really good about where we are set up (Kalshi, Polymarket - 90% of volume is sports)
> Vertically inregrated to own the stack: own control of breadth and depth we heard from customers

---

## Matthew Smith — Staff Data Analyst 12:45

**Org:** Rolls up to Product Analytics leadership. Michael Byman is his manager.
Core Value: **Be A Great Teammate**

### Focus Areas

* Can you work with analysts/business partners and deeply understand workflows?
* How do you work with analysts, and would you be a great teammate to work with?

### Example Questions

> Walk me through a workflow tool or process that improved analyst quality of life.
* Subway rebates

> Walk me through your approach to defining a key business metric when multiple teams disagree on the definition.
* Show what the metric output looks like using A and B
  * If the output is very close -- who cares?? Perfection vs progress
* Get in a room and talk about it
* If all else fails, escalate
  * I like the single-metric-champion approach
* Seek to understand intent: could it be two different but similar metrics?
  * Reschedule vs Truck-roll vs CNC metrics

> How do you make your data assets intuitive for business users who are non-technical?
* For data models, say at the Gold layer especially where you might have semi-technical users querying or dashboard building off of, capture very clear definitions in the metadata, bias naming towards business terminology rather than source system names, use filters that make sense based on context e.g. pre-filter out deleted records instead of keeping inside a Gold layer model (unless relevant)
  * Make very clear if a dim is temporal or "current"
* For dashboards, use common features across dashboards (e.g. train users to expect to see the same drill-down functionality across similar dashboards), maybe record a video demo and embed in the dashboard for anything particularly bespoke
* For conversational analytics, setting up the agent w/ clear metric definitions, access to all the expected dimensions and filters in the semantic layer, and improving over time by automating updates based on real chat interactions and user feedback.

### Notes From Conversation
>
---

**There are no tricks.**



other notes:
"That's all Skills are, organized folders with scripts as tools" - Barry Z