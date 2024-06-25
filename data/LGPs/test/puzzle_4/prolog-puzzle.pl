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
all_members([24, 27, 30, 33], [A0, A1, A2, A3]),
member([C0_val, c0], All),
member([C2_val, c2], All),
C0_val-C2_val=:=3,
A0-A1=:=6,
or([and([A3 = 33,member([27, c3], All)]),and([member([33, c3], All),A3 = 27])]),
and([or([member([33, c3], All),C2 = c3]), not(and([member([33, c3], All),C2 = c3]))]).
