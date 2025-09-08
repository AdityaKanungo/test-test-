Core

case_hdr → application (join on case_id)

case_hdr → case_comment (join on case_id)

case_hdr → case_lock (join on case_id)

case_hdr → case_address (join on case_id)

case_address → address (join on address_id)


Applications & Household

application → application_household (join on application_id)

application → email (join on application_id)

application → phone (join on application_id)


Individuals

application_household → individual (join on application_household_id)

application_household.head_individual_id → individual.individual_id (head pointer)

individual → individual_detail (join on individual_id)

individual → lu_household_relation (join on household_relation_id)


Race

individual → individual_race (join on individual_id)

individual_race → lu_race (join on race_id)


Benefits

application_household → individual_benefit (join on application_household_id)

individual → individual_benefit (join on individual_id)

individual_benefit → lu_benefit_type (join on benefit_type_id)


Financials

individual → resource (join on individual_id)

individual → expense (join on individual_id)

individual → income (join on individual_id)

income → earned_income (join on income_id)

income → unearned_income (join on income_id)
