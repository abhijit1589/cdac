######################Q.1##############################


CREATE TABLE Customer2 (
    customer_id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT CHECK (age >= 18),
    mobile_no int UNIQUE,
    address varchar(20)

);

##############################Q.2###################

insert into customer2 values
(1,"Abhijit",23,77108324,"mumbai"),
(2,"Shrikant",26,88108321,"kharghar"),
(3,"Amay",20,98458360,"panvel");
################################Q.3############################
use hr;
select * from employees;
select first_name from employees where length(first_name)=4;

##########################Q.4######################
select sum(salary), department_id from employees 
group by department_id;
###################Q.5##############################

select * from employees where department_id in
(select avg(salary) from employees
group by department_id
having avg(salary)>75000);



#####################Q.6###############################
select * from countries;
select * from locations;

select c.region_id, count(l.city) as no_ofcity from countries c 
join locations l on l.country_id=c.country_id
group by region_id
order by no_ofcity desc
limit 1;

##################Q.7#####################################
select * from employees;
 delimiter //
 create procedure detail(in emp_id int)
 deterministic
 begin
 select group_concat(concat(e.first_name,' ',e.last_name),'  ',d.department_name,e.hire_date)as detail from employees e
 join departments d on d.department_id=e.department_id;
 end //
 delimiter ;
 
  call detail(100);
  
#########################Q.8#########################################

delimiter //
create function experience_years( emp_id int)
returns int
deterministic
begin
declare experience int;
select datediff(current_date,hire_date)/365 into experience from employees 
where employee_id=emp_id;
return experience;
end //
delimiter ;

select experience_years(100);
##################################################################
#MongoDb
##############################Q.1######################################


db.resturant.find({ "name": /^P/ });

#####################################Q.2######################################################
 
 
db.resturant.find({ "cuisine": { "$in": ["bakery", "Chinese"] } });

#####################################Q.3#################################################

 db.resturant.find({ "grades.score": { $gt: 20, $eq: 100 } });

  
