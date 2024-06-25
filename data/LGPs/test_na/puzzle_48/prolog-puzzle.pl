all_members([H], L) :- member(H, L).
all_members([H|T], L) :- member(H, L), all_members(T, L).

all_not_members([H], L) :- not(member(H, L)).
all_not_members([H|T], L) :- not(member(H, L)), all_not_members(T, L).

and([H]) :- H.
and([H|T]) :- H, and(T).

or([H]) :- H, !.
or([H|_]) :- H, !.
or([_|T]) :- or(T).

solve(B0,B1,B2,B3) :-
B0 = [A0, C0],
B1 = [A1, C1],
B2 = [A2, C2],
B3 = [A3, C3],

All = [B0,B1,B2,B3],

all_members([c0, c1, c2, c3], [C0, C1, C2, C3]),
all_members([2016, 2017, 2018, 2019], [A0, A1, A2, A3]),
and([or([A2 = 2019,A2 = 2016]), not(and([A2 = 2019,A2 = 2016]))]),
or([and([C1 = c0,member([2017, c3], All)]),and([member([2017, c0], All),C1 = c3])]),
member([C1_val, c1], All),
C1_val<A3,
or([and([C0 = c1,A2 = 2018]),and([C2 = c1,A0 = 2018])]),
C3 = c0.
