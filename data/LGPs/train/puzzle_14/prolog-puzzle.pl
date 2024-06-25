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
all_members([6, 8, 10, 12], [A0, A1, A2, A3]),
member([12, c1], All),
and([or([A0 = 10,C0 = c2]), not(and([A0 = 10,C0 = c2]))]),
member([C2_val, c2], All),
A2-C2_val=:=4,
and([or([A1 = 10,C1 = c2]), not(and([A1 = 10,C1 = c2]))]),
member([C0_val, c0], All),
A1-C0_val=:=2.
