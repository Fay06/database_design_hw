queries = ["" for i in range(0, 9)]

### 0. List all the users who were born in 1998.
### Output column order: userid, name, birthdate, joined
### Order by birthdate ascending
queries[0] = """
select userid, name, birthdate, joined
from users
where extract(year from birthdate) = 1998 
order by birthdate asc;
"""

### 1. Write a single query to rank the "groups" by the number of members, with the group 
### with the highest number of members getting rank 1. 
### If there are ties, the two (or more) groups should get the same "rank", and next ranks 
### should be skipped.
###
### HINT: Use a WITH clause to create a temporary table (temp(groupname, num_members) 
### followed by the appropriate "RANK"
### construct -- PostgreSQL has several different
### See: https://www.eversql.com/rank-vs-dense_rank-vs-row_number-in-postgresql/, for some
### examples.
### PostgreSQL documentation has a more succinct discussion: https://www.postgresql.org/docs/current/functions-window.html
###
### Output Columns: groupname, rank
### Order by: rank, groupname ascending
queries[1] = """
with temp as (
    select groupid, count(*) as num_members
    from members
    group by groupid
)
select (select name from groups where groups.groupid = temp.groupid) as groupname, RANK() OVER(ORDER BY num_members desc) as rank
from temp
order by rank, groupname asc;
"""

### 2. Use window functions to construct a query to associate the average number
### followers for each "joined" year, with each user.
###
### See here for a tutorial on window functions: https://www.postgresql.org/docs/current/tutorial-window.html
###
### We have created a table using WITH for you: temp(userid, name, joinedyear, num_followers)
### Our goal is to create a new table with columns: (userid, name, joinedyear, num_followers, avg_num_followers_for_that_year)
### Here: avg_num_followers_for_that_year is basically the average number of followers across
### all users who joined in that year
###
### This kind of an output table will allow us to compare each user with the other users 
### who joined in that same year (e.g., to understand whether popularity is correlated with how
### long the user has been on the social network)
### Order by: joined_year first, and then userid
queries[2] = """
with temp as (
        select userid, name, extract(year from joined) as joined_year, 
               (select count(*) from follows where follows.userid2 = users.userid) as num_followers
        from users
        )
select userid, name, joined_year, num_followers, avg(num_followers) OVER (PARTITION BY joined_year)
from temp
order by joined_year, userid asc;
"""

### 3. Similar to the above, but here the goal is to create the following table:
###
### Output columns: (userid, name, num_status_updates, num_followers, avg_num_followers_for_that_status_update, rank by num_followers within users with the same num_status_updates)
###
### As above, use WITH to create a temp table with columns: (userid, name, num_status_updates, num_followers), and then use two WINDOW functions, one for average and one for RANK.
###
### Order by: num_status_updates, rank, userid
###
### First few rows of the result look like this:
### The "rank" here would be the rank within the counties for that state.
### user134 | Ronald Miller       |                  0 |            15 |                       8.3750000000000000 |    1
### user12  | Carol Lopez         |                  0 |            12 |                       8.3750000000000000 |    2
### user54  | Helen Lee           |                  0 |            11 |                       8.3750000000000000 |    3

queries[3] = """
with temp as(
    select userid, name, (select count(*) from status where status.userid = users.userid) as num_status_updates,
    (select count(*) from follows where follows.userid2 = users.userid) as num_followers
    from users
)
select userid, name, num_status_updates, num_followers,
avg(num_followers) OVER (PARTITION BY num_status_updates) as avg_num_followers_for_that_status_update,
RANK() OVER (PARTITION BY num_status_updates ORDER BY num_followers desc) as rank
from temp
order by num_status_updates, rank, userid asc;
"""


### 4. Write a function that takes in a userid as input, and returns the number of friends for
### that user.
###
### Function signature: num_friends(in varchar, out num_friends bigint)
###
### There are several examples here at the bottom: https://www.postgresql.org/docs/10/sql-createfunction.html
### You should be writing one that uses SQL, i.e., has "LANGUAGE SQL" at the end.
### 
### So calling num_friends('user0') should return 21. Make sure your function returns 0
### appropriately (for users who do not have any friends).
### 
### Confirm that the query below works after the function is created:
###             select userid, name, num_friends(userid) from users
###
queries[4] = """
CREATE FUNCTION num_friends(in varchar, out num_friends bigint)
    AS $$ select count(distinct userid2) from Friends where userid1 = $1 $$
    LANGUAGE SQL;
"""

### 5. Write a function that takes in an userid as input, and returns a JSON string with 
### the details of friends and followers of that user.
###
### So SQL query: select user_details('user0');
### should return a single tuple with a single attribute of type string/varchar as:
### { "userid": "user0", "name": "Anthony Roberts", "friends": [{"name": "Anthony Taylor"}, {"name": "Betty Garcia"}, {"name": "Betty Hernandez"}, {"name": "Betty Lewis"}, {"name": "Betty Lopez"}, {"name": "Betty Parker"}, {"name": "Betty Thomas"}, {"name": "Brian Jackson"}, {"name": "Brian King"}, {"name": "Brian Robinson"}, {"name": "Daniel Lewis"}, {"n ame": "Deborah Turner"}, {"name": "Donald Adams"}, {"name": "Donald Thompson"}, {"name": "Donald Walker"}, {"name": "Dorothy Gonzalez"}, {"name": "James Mitchell"}, {"name": "Ja son Phillips"}, {"name": "Jeff White"}, {"name": "Kevin Allen"}, {"name": "Kimberly Allen"}], "follows": [{"name": "Betty Thomas"}, {"name": "David Anderson"}, {"name": "Edward Green"}, {"name": "Elizabeth Jones"}, {"name": "Nancy Gonzalez"}, {"name": "Richard Perez"}, {"name": "Ronald Garcia"}]}
###
### Within "friends" and "follows", the entries should be ordered by name.
###
### You should use PL/pgSQL for this purpose -- writing this purely in SQL is somewhat cumbersome.
### i.e., your function should have LANGUAGE plpgsql at the end.
###
### Function signature: user_details(in varchar, out details_json varchar)
###
### HINT: Use "string_agg" aggregate functions for creating the two lists properly: https://www.postgresqltutorial.com/postgresql-aggregate-functions/postgresql-string_agg-function/
### Use "CONCAT()" function for concatenating (or you can use ||).
###
### BE CAREFUL WITH WHITE SPACES -- we will remove any spaces before comparing answers, but there is
### still a possibility that you fail comparisons because of that.
queries[5] = """
CREATE OR REPLACE FUNCTION user_details(in varchar, out details_json varchar)
    AS $$
    
    begin
    with temp1 as(
        select name
        from users
        where users.userid in (select userid2 from friends where userid1 = $1)
        order by name asc
    ),
    temp2 as(
        select name
        from users
        where users.userid in (select userid1 from follows where userid2 = $1)
        order by name asc
    )
    select '{ "userid": ' || '"' || $1 || '", ' || '"name": ' || '"' || (select name from users where userid = $1) || '", ' ||
        '"friends": [' || (select STRING_AGG('{"name": "' || temp1.name || '"}', ', ') friends from temp1) || '], '
        '"follows": [' || (select STRING_AGG('{"name": "' || temp2.name || '"}', ', ') follows from temp2) || ']}'
         INTO details_json;
    return;
    end
        
    $$
    LANGUAGE plpgsql;
"""

### 6. Create a new table using:
###         create table influencers as
###             select u.userid, u.name, count(userid1) as num_followers
###             from users u join follows f on (u.userid = f.userid2)
###             group by u.userid, u.name
###             having count(userid1) > 10;
###
### Create a new trigger that: 
###         When a tuple is inserted in the follows relation, appropriately modifies influencers.
###         Specifically:
###             If the userid2 for the new follows tuple is already present in influencers,
##                  then the num_followers should be increased appropriately.
###             If the userid2 for the new follows tuple is NOT present in influencers, 
###                 then it should check whether the addition of the new follower makes the user
###                 an influencer, and add the entry to influencers table.
###
###  As per PostgreSQL syntax, you have to write two different statements -- queries[6] should be the CREATE FUNCTION statement, 
###  and queries[7] should be the CREATE TRIGGER statement.
###
###  We have provided some partial syntax.
###
### You can find several examples of how to write triggers at: https://www.postgresql.org/docs/10/sql-createtrigger.html, and a full example here: https://www.tutorialspoint.com/postgresql/postgresql_triggers.htm
queries[6] = """
CREATE OR REPLACE FUNCTION update_influencers_on_insert()
    RETURNS TRIGGER
    LANGUAGE PLPGSQL
    AS
    $$
    BEGIN
        IF ((select count(userid1) from follows where userid2 = new.userid2) > 10) THEN
            IF (select NOT EXISTS (select * from influencers where userid = new.userid2)) THEN
                INSERT INTO influencers (userid, name, num_followers) VALUES(new.userid2, (select name from users where userid = new.userid2), (select count(userid1) from follows where userid2 = new.userid2));
            ELSE
                UPDATE influencers SET num_followers = (select count(userid1) from follows where userid2 = new.userid2) where userid = new.userid2;
            END IF;
        END IF;
        RETURN NEW;
    END
    $$;
"""

queries[7] = """
CREATE TRIGGER check_update
    AFTER INSERT ON follows
    FOR EACH ROW
    EXECUTE PROCEDURE update_influencers_on_insert();
"""


### 8. Recursion can be used in our database to find all users a user is connected with through
### others (i.e., friends of friends, friends of friends of friends, etc).
### 
### However, our friends table has so much connectivity that the result is somewhat meaningless
### (everyone is connected to everyone). 
###
### Hence, we will use a smaller friends table for this query.
### Use the following query to create a smaller friends table:
###        select f.userid1, f.userid2 into friends_small from friends f, users u1, users u2 where f.userid1 = u1.userid and f.userid2 = u2.userid and abs(extract(year from u1.birthdate) - extract(year from u2.birthdate)) < 5;
### 
### Complete the below partial query to find all the other users that they are
### connected to through other users through the "friends_small" table.
###
### Make sure you don't list a user as their own friend.
###
### There should be 1972 rows in the output.
###
### Output columns: name1, userid1, name2, userid2
### Output order: name1, name2
###
### MAKE SURE YOU ARE USING FRIENDS_SMALL IN YOUR QUERY -- WE WILL CREATE THAT TABLE IN OUR TEST DATABASE
###
queries[8] = """
with recursive temp(name1, userid1, name2, userid2) as
(
    select (select name from users where userid = userid1) as name1, userid1, (select name from users where userid = userid2) as name2, userid2
    from friends_small
  union
    select temp.name1, temp.userid1, (select name from users where userid = friends_small.userid2) as name2, friends_small.userid2
    from friends_small, temp
    where temp.userid2 = friends_small.userid1 and temp.userid1 != friends_small.userid2
 )
select *
from temp
order by name1, name2 asc;
"""
