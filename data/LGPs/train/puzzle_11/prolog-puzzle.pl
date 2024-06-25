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
all_members([25, 30, 35, 40], [A0, A1, A2, A3]),
and([or([member([25, c0], All),C0 = c0]), not(and([member([25, c0], All),C0 = c0]))]),
C0 = c1,
and([or([member([40, c2], All),C3 = c2]), not(and([member([40, c2], All),C3 = c2]))]),
member([C2_val, c2], All),
C2_val-A1=:=10,
A1 = 30.
