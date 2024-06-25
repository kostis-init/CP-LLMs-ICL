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
all_members([45, 60, 75, 90], [A0, A1, A2, A3]),
A0<A2,
and([or([member([90, c0], All),member([90, c1], All)]), not(and([member([90, c0], All),member([90, c1], All)]))]),
member([C3_val, c3], All),
C3_val>A2,
or([and([C0 = c1,A2 = 45]),and([A0 = 45,C2 = c1])]),
not(A3 = 60),
not(A3 = 45),
not(A3 = 90).
