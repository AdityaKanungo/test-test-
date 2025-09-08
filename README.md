---

Core

case_hdr (1) → (∗) application
application.case_id = case_hdr.case_id

case_hdr (1) → (∗) case_comment
case_comment.case_id = case_hdr.case_id

case_hdr (1) → (∗) case_lock
case_lock.case_id = case_hdr.case_id

case_hdr (1) → (∗) case_address
case_address.case_id = case_hdr.case_id

address (1) → (∗) case_address
case_address.address_id = address.address_id



---

Applications & Household

application (1) → (1) application_household
application_household.application_id = application.application_id

application (1) → (∗) email
email.application_id = application.application_id

application (1) → (∗) phone
phone.application_id = application.application_id



---

Individuals & Household

application_household (1) → (∗) individual
individual.application_household_id = application_household.application_household_id

application_household (1) → (1) head_individual (head pointer)
application_household.head_individual_id = individual.individual_id
(Head must be one of the individuals in the same household.)

individual (1) → (1) individual_detail
individual_detail.individual_id = individual.individual_id

lu_household_relation (1) → (∗) individual
individual.household_relation_id = lu_household_relation.household_relation_id



---

Race (bridge)

individual (1) → (∗) individual_race
individual_race.individual_id = individual.individual_id

lu_race (1) → (∗) individual_race
individual_race.race_id = lu_race.race_id
(This forms M:N between individual and lu_race via individual_race.)



---

Benefits

application_household (1) → (∗) individual_benefit
individual_benefit.application_household_id = application_household.application_household_id

individual (1) → (∗) individual_benefit
individual_benefit.individual_id = individual.individual_id

lu_benefit_type (1) → (∗) individual_benefit
individual_benefit.benefit_type_id = lu_benefit_type.benefit_type_id



---

Financials

individual (1) → (∗) resource
resource.individual_id = individual.individual_id

individual (1) → (∗) expense
expense.individual_id = individual.individual_id

individual (1) → (∗) income
income.individual_id = individual.individual_id

income (1) → (0/1) earned_income
earned_income.income_id = income.income_id

income (1) → (0/1) unearned_income
unearned_income.income_id = income.income_id
(Each income is either earned or unearned, not both.)
