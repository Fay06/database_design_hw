queries = ["" for i in range(0, 25)]

### 0. List all the users who were born in 1998.
### Output column order: userid, name, birthdate, joined
### Order by birthdate ascending
queries[0] = """
select userid, name, birthdate, joined
from users
where extract(year from birthdate) = 1998 
order by birthdate asc;
"""

### 1. Report the user information (userid, name, birthdate, joined) for all users with first name 'Carol'. (Hint: use ``like'').
### Output column order: userid, name, birthdate, joined
### Order by birthdate ascending
queries[1] = """
select userid, name, birthdate, joined
from users
where name LIKE 'Carol%'
order by birthdate asc;
"""


### 2. Write a query to output the age (in years) for every user when they joined the social network.
### Use 'age' function that operates on dates (https://www.postgresql.org/docs/12/functions-datetime.html)
### Output columns: name, age
### Order output by age increasing
### The first row in the output should be: (Jason Phillips, 6)
queries[2] = """
select name, extract (year from age(joined, birthdate)) as age
from users
order by age(joined, birthdate) asc;
"""

### 3. Select all the "distinct" years that users with names starting with 'M' are born in.
### Output column: year
### Order output by year ascending
queries[3] = """
select distinct extract (year from birthdate)
from users
where name LIKE 'M%'
order by extract (year from birthdate) asc;
"""

### 4. Write a query to find users who have been on the social network for more than half their life as of 'August 31, 2021'.
### Use 'age' function as above.
### Output columns: name
### Order by name ascending
queries[4] = """
select name
from users
where age('August 31, 2021', joined) * 2 >= age('August 31, 2021', birthdate)
order by name asc;
"""

### 5. Write a single query to report all status updates for  the user 'Kevin Allen' by joining status and user.
### Output Column: status_time, text
### Order by: status_time increasing
queries[5] = """
select status_time, text
from users natural join Status
where name = 'Kevin Allen'
order by status_time asc;
"""

### 6. Write a query to find all users who satisfy one of the following conditions:
###        - the user's name starts with a 'J' and they were born before and including 1980
###        - the user's name starts with an 'M' and they were born after 1980 (excluding 1980)
### Output columns: name, birthdate
### Order by: name ascending
queries[6] = """
select name, birthdate
from users
where (name like 'J%' and extract (year from birthdate) <= 1980) or (name like 'M%' and extract (year from birthdate) > 1980)
order by name asc;
"""


### 7. Count the number of the friends of the user 'Kevin Allen'.
### Output columns: num_friends
queries[7] = """
select count(distinct userid2)
from Friends
where userid1 in
(select userid
from users
where name = 'Kevin Allen');
"""

### 8. Count the total number of users whose names start with a vowel ('A', 'E', 'I', 'O', 'U'). (Hint: Use "in" and "substr").
### Output columns: numusers
queries[8] = """
select count(name)
from users
where substr(name, 1, 1) in ('A', 'E', 'I', 'O', 'U');
"""


### 9. SQL "with" clause can be used to simplify queries. It essentially allows
### specifying temporary tables to be used during the rest of the query. See Section
### 3.8.6 (6th Edition) for some examples.
###
### Write a query to find the name(s) of the user(s) with the largest number of friends. We have provided
### a part of the query to build a temporary table.
###
### Output columns: name, num_friends 
### Order by name ascending (there may be more than one answer)
queries[9] = """
with temp as (
        select name, count(*) as num_friends 
        from users, friends 
        where users.userid = friends.userid1 
        group by name)
select *
from temp
where num_friends = (select max(num_friends) from temp)
order by name asc;
"""



### 10. List the names of the users who posted no status updates. Hint: Use "not in".
### Output Columns: name
### Order by name ascending
queries[10] = """
select name
from users
where userid not in (select userid from status)
order by name asc;
"""


### 11. Write a query to output a list of users and their friends, such that the friend has an
### upcoming birthday within next 15 days.  Assume today is Sept 10, 2021
### (so look for birthdays between Sept 11 and Sept 25, both inclusive). You can hardcode
### that if you'd like.
### Output: username, friendname, friendbirthdate
### Order by: username, friendname ascending
queries[11] = """
with temp1 as (
        select name as friendname, userid, birthdate as friendbirthdate
        from users
        where (extract (month from birthdate) = 9 and (extract (day from birthdate) > 10 and extract (day from birthdate) < 26))
        ),
temp2 as (
        select userid2 as tempuserid, friendname, friendbirthdate
        from friends, temp1
        where friends.userid1 = temp1.userid
        )
select name as username, friendname, friendbirthdate
from users, temp2
where users.userid = temp2.tempuserid
Order by username, friendname asc;
"""


### 12. For each user who has posted at least two status updates, count the
### average amount of time between his or her status updates in seconds.
### Order the results in the increasing order by the userid.
###
### Hint: Date substraction returns the amount in (fractional) number of days. 
### Hint 2: The number of seconds in a day is 86400.
### Hint 3: Use "having" to find users who have at least 2 status updates.
###
### Output columns: userid, gapseconds
### Order by: userid
queries[12] = """
select users.userid as userid, (max(status_time) - min(status_time)) * 86400 / (count(*) - 1)
from users, status
where users.userid = status.userid
group by users.userid
having count(statusid) >= 2
order by userid asc;
"""


### 13. Generate a list - (birthyear, num-users) - containing the years
### in which the users in the database were born, and the number of users
### born in each year.
###
### You don't need to worry about years where no users were born, i.e., there should
### not be any entries for years where no one in the database was born.
###
### Output columns: birthyear, num_users
### Order by birthyear
queries[13] = """
select extract (year from birthdate) as birthyear, count(1) as num_users
from users
group by birthyear
order by birthyear;
"""

### 14. Generate a list - (birthyear, num-users) - containing the years
### in which the users in the database were born, and the number of users
### born in each year.
###
### However, your output here should have all years between 1940 and 2000 both inclusive, 
### with 0 counts if no users were born that year
###
### HINT: Use "generate_series()" to create an inline table -- try 
### "select * from generate_series(1, 10) as g(n);" to see how it works.
### This is what's called a "set returning function", and the result can be used as a relation.
### See: https://www.postgresql.org/docs/12/functions-srf.html
###
### Output columns: birthyear, num_users
### Order by birthyear
queries[14] = """
with temp1 as (
    select extract (year from birthdate) as birthyear, count(1) as num_users
    from users
    group by birthyear
),
temp2 as (
    select birthyear, 0 as num_users
    from generate_series(1940, 2000) as birthyear
)
select temp2.birthyear, greatest(temp1.num_users, temp2.num_users)
from temp2 left join temp1 on temp1.birthyear = temp2.birthyear
order by temp2.birthyear asc;
"""

### 15. Find the name of the group with the maximum number of members. There may be more than one answer.
###
### Output: name, num_members
### Order by name ascending
queries[15] = """
with temp as (
        select groupid, count(1) as num_members
        from members
        group by groupid)
select name, num_members
from groups, temp
where num_members = (select max(num_members) from temp) and groups.groupid = temp.groupid
order by name asc;
"""

### 16. Write a query to find the names of all users that "Michael Smith" is friends with or follows.
### The output should be a list of names, with a second column that takes values: "friends", or "follows"
### Some names might appear twice
###
### HINT: Use "union"
### HINT 2: Note that constants can be hardcoded in the select cause (e.g., try "select userid, 'hi' from users;")
###
### Output columns: name, type -- type takes values "friends" or "follows"
queries[16] = """
(with temp1 as (
    select userid2
    from Friends
    where userid1 in
    (select userid
    from users
    where name = 'Michael Smith')
)
select name, 'friends'
from users, temp1
where userid = userid2
)
union
(
with temp2 as (
    select userid2
    from Follows
    where userid1 in
    (select userid
    from users
    where name = 'Michael Smith')
)
select name, 'follows'
from users, temp2
where userid = userid2
);
"""


### 17. Write a query to count for each user, the number of other users that they are both friends with and follow.
###
### HINT: Use "intersection" on "friends" and "follows" as a starting point.
###
### Output columns: userid, name, num_common
### Order by name ascending
queries[17] = """
with temp as(
    (select name, userid, userid2
    from users, friends
    where userid1 = userid
    ) intersect (
    select name, userid, userid2
    from users, follows
    where userid1 = userid)
)
select userid, name, count(userid2) as num_common
from temp
group by userid, name
Order by name asc;
"""

### 18. Find the pairs of users that were born closest to each other (there are no two users with the
### same birthdate). There may be multiple answers.
###
### For any pair, the output should only contain one row such that username1 < username2
###
### Output columns: username1, username2 
### Order by: username1
queries[18] = """
with temp1 as (
    select name as username2, birthdate, lead(birthdate) over (order by birthdate) temp_birthdate, lead(name) over (order by birthdate) username1
    from users
),
temp2 as (
    select username1, username2, (temp_birthdate - birthdate) as diff
    from temp1
)
select username1, username2
from temp2
where diff = (select min(diff) from temp2)
order by username1 asc;
"""

### 19. For each user, calculate the number of friends and the number of followers.
### Note that a user with no friends will not appear in the friends table, and same
### goes for follows table. But 0 counts should still be appropriately recorded.
###
### Output columns: userid, name, num_friends, num_followers
### Order by: userid
queries[19] = """
with temp as (
    select userid, 0 as num_friends, 0 as num_followers
    from users
),
temp1 as (
    select userid1 as userid, count(userid2) as num_friends, 0 as num_followers
    from friends
    group by userid1
),
temp2 as (
    select userid2 as userid, 0 as num_friends, count(userid1) as num_followers
    from follows
    group by userid2
),
temp3 as (
    select temp.userid, greatest(temp.num_friends, temp1.num_friends) as num_friends, greatest(temp.num_followers, temp1.num_followers) as num_followers
    from temp1 right join temp on temp.userid = temp1.userid
)
select temp3.userid, name, greatest(temp3.num_friends, temp2.num_friends) as num_friends, greatest(temp3.num_followers, temp2.num_followers) as num_followers
from users, temp2 right join temp3 on temp3.userid = temp2.userid
where users.userid = temp3.userid
order by temp3.userid asc;
"""


### 20. Find all users who are not followed by anyone who is a member of the group: 
### 'University of Maryland, College Park USA'
### You can hard code the group id: 'group36'
###
### HINT: Use Set Operation "Not Exists"
###
### Output column order: name
### Order by name ascending
queries[20] = """
with temp1 as (
    select distinct userid2
    from follows
    where userid1 in (select userid
    from members
    where groupid = 'group36')
),
temp2 as (
    select userid
    from users
    where userid not in (select userid2 from temp1)
)
select name
from users, temp2
where users.userid = temp2.userid
order by name asc;
"""


### 21. Create a copy of the "users" table using the following command:
### select * into userscopy from users, OR
### create table userscopy as (select * from users)
###
### For the next few questions, we will use this duplicated table
###
### Write a single query/statement to add two new columns to the "users" table -- age (integer), and usage (varchar(10)).
queries[21] = """
alter table userscopy add age INT, add usage varchar(10);
"""

### 22. Write a single query/statement to set the values of both of the new columns. Use "age()" function to find the 
### age in years (as we did above) as of "August 31, 2021". 
###
### The "usage" column takes three values: "heavy", "medium", "light"
### The usage is "heavy" if the total number of status updates > 10, "medium" if 5 <= # status updates <= 10, and "light" if < 5.
###
### HINT: Use a "with" clause to create a temporary table with the counts, and use CASE to simplify the update.
###
### NOTE: You need to account for users with no status updates in 'status' table
queries[22] = """
with temp as (
    select userid, count(userid) as num_status
    from status
    where userid in (select userid from users)
    group by userid
)
update userscopy
set age = extract (year from age('August 31, 2021', birthdate)),
    usage = CASE when (select num_status from temp where userscopy.userid = temp.userid) > 10 then 'heavy'
                when (select num_status from temp where userscopy.userid = temp.userid) >= 5 then 'medium'
                when (select num_status from temp where userscopy.userid = temp.userid) < 5 then 'light'
                when (select num_status from temp where userscopy.userid = temp.userid) is null then 'light'
            END;
"""


### 23. Write a query "delete" all users from userscopy who were born in May.
queries[23] = """
delete from userscopy
where extract (month from birthdate) = 5;
"""


### 24. Use "generate_series" as above to write a single statement to insert 10 new tuples
### to 'userscopy' of the form:
### ('newuser11', 'New User 11', '1990-01-11', '2015-01-11', 0, 'light')
### ('newuser12', 'New User 12', '1990-01-12', '2015-01-12', 0, 'light')
### ...
### ('newuser20', 'New User 20', '1990-01-20', '2015-01-20', 0, 'light')
###
### HINT: Use concatenation operator: 'newuser' || 0, and addition on dates to simplify.
queries[24] = """
insert into userscopy values ('newuser11', 'New User 11', '1990-01-11', '2015-01-11', 0, 'light'), ('newuser12', 'New User 12', '1990-01-12', '2015-01-12', 0, 'light'), ('newuser13', 'New User 13', '1990-01-13', '2015-01-13', 0, 'light'), ('newuser14', 'New User 14', '1990-01-14', '2015-01-14', 0, 'light'), ('newuser15', 'New User 15', '1990-01-15', '2015-01-15', 0, 'light'), ('newuser16', 'New User 16', '1990-01-16', '2015-01-16', 0, 'light'), ('newuser17', 'New User 17', '1990-01-17', '2015-01-17', 0, 'light'), ('newuser18', 'New User 18', '1990-01-18', '2015-01-18', 0, 'light'), ('newuser19', 'New User 19', '1990-01-19', '2015-01-19', 0, 'light'), ('newuser20', 'New User 20', '1990-01-20', '2015-01-20', 0, 'light');
"""
