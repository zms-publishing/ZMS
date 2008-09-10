# http://gadfly.sourceforge.net/gadfly.html
drop table cds;
create table cds (cd_id integer, cd_title varchar, cd_cover varchar);
insert into cds(cd_id, cd_title, cd_cover) values (4711, 'Pink Floyd: The dark side of the moon', '');
insert into cds(cd_id, cd_title, cd_cover) values (4712, 'Rolling Stones: A Bigger Bang', '');
create table cdtracks (cd_id integer, track_id integer, track_title varchar, track_duration varchar, track_info varchar, sort_id integer);
insert into cdtracks (cd_id, track_id, track_title, track_duration, track_info, sort_id) values ( 4711, 1, 'Speak to Me', '1:30', 'Nick Mason', 10);
insert into cdtracks (cd_id, track_id, track_title, track_duration, track_info, sort_id) values ( 4711, 2, 'Breathe', '2:43', 'David Gilmour, Roger Waters, Richard Wright', 20);
insert into cdtracks (cd_id, track_id, track_title, track_duration, track_info, sort_id) values ( 4711, 3, 'On the Run', '3:30', 'Gilmour, Waters', 30);
insert into cdtracks (cd_id, track_id, track_title, track_duration, track_info, sort_id) values ( 4711, 4, 'Time', '6:53', 'Gilmour, Waters, Wright, Mason', 40);
insert into cdtracks (cd_id, track_id, track_title, track_duration, track_info, sort_id) values ( 4712, 5, 'Rough Justice', '3:13', '', 10);
insert into cdtracks (cd_id, track_id, track_title, track_duration, track_info, sort_id) values ( 4712, 6, 'Let Me Down Slow', '4:15', '', 20);
insert into cdtracks (cd_id, track_id, track_title, track_duration, track_info, sort_id) values ( 4712, 7, 'It Wont Take Long', '3:54', '', 30);
insert into cdtracks (cd_id, track_id, track_title, track_duration, track_info, sort_id) values ( 4712, 8, 'Rain Fall Down', '4:54', '', 40);
insert into cdtracks (cd_id, track_id, track_title, track_duration, track_info, sort_id) values ( 4712, 9, 'Streets of Love', '5:10', '', 50);
