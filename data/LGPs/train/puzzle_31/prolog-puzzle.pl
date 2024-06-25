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
all_members([181, 184, 187, 190], [A0, A1, A2, A3]),
member([C3_val, c3], All),
member([C1_val, c1], All),
C3_val>C1_val,
member([C0_val, c0], All),
member([C1_val, c1], All),
C1_val-C0_val=:=3,
A3<A1,
and([or([C2 = c1,C2 = c2]), not(and([C2 = c1,C2 = c2]))]),
or([and([A0 = 184,C3 = c3]),and([C0 = c3,A3 = 184])]).
