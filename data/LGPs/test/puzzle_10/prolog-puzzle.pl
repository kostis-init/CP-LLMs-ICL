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
all_members([2007, 2008, 2009, 2010], [A0, A1, A2, A3]),
C2 = c0,
and([or([A0 = 2007,A0 = 2009]), not(and([A0 = 2007,A0 = 2009]))]),
member([C3_val, c3], All),
member([C2_val, c2], All),
C3_val<C2_val,
member([C0_val, c0], All),
C0_val-A3=:=1,
not(A1 = 2007),
not(A1 = 2009),
not(C1 = c2),
not(member([2007, c2], All)),
not(member([2009, c2], All)).
