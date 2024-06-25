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
all_members([1, 2, 3, 4], [A0, A1, A2, A3]),
or([and([member([4, c3], All),C3 = c0]),and([C3 = c3,member([4, c0], All)])]),
A2<A3,
C1 = c1,
and([or([member([2, c0], All),member([2, c1], All)]), not(and([member([2, c0], All),member([2, c1], All)]))]),
or([and([A2 = 2,C3 = c2]),and([A3 = 2,C2 = c2])]).
