function mpc = case12da
%CASE12DA  Power flow data for 12 bus distribution system from Das, et al
%   Please see CASEFORMAT for details on the case file format.
%
%   Data from ...
%       D. Das, H.S. Nagi, D.P. Kothari, "Novel method for solving radial
%       distribution networks", IEE Proc. C, Vol. 141, No. 4, pp. 291-298, 1994.
%
%   Plain-data copy of benchmark-grids/matpower/case12da.m: the file's
%   MATLAB statements (below, as they were) are evaluated by
%   scripts/evaluate_matpower_code.py and the matrices hold the result.
%     Vbase = mpc.bus(1, BASE_KV) * 1e3;
%     Sbase = mpc.baseMVA * 1e6;
%     mpc.branch(:, [BR_R BR_X]) = mpc.branch(:, [BR_R BR_X]) / (Vbase^2 / Sbase);
%     mpc.bus(:, [PD, QD]) = mpc.bus(:, [PD, QD]) / 1e3;

%% MATPOWER Case Format : Version 2
mpc.version = '2';

mpc.baseMVA = 1;

mpc.bus = [
	1	3	0	0	0	0	1	1	0	11	1	1	1;
	2	1	0.06	0.06	0	0	1	1	0	11	1	1.1	0.9;
	3	1	0.04	0.03	0	0	1	1	0	11	1	1.1	0.9;
	4	1	0.055	0.055	0	0	1	1	0	11	1	1.1	0.9;
	5	1	0.03	0.03	0	0	1	1	0	11	1	1.1	0.9;
	6	1	0.02	0.015	0	0	1	1	0	11	1	1.1	0.9;
	7	1	0.055	0.055	0	0	1	1	0	11	1	1.1	0.9;
	8	1	0.045	0.045	0	0	1	1	0	11	1	1.1	0.9;
	9	1	0.04	0.04	0	0	1	1	0	11	1	1.1	0.9;
	10	1	0.035	0.03	0	0	1	1	0	11	1	1.1	0.9;
	11	1	0.04	0.03	0	0	1	1	0	11	1	1.1	0.9;
	12	1	0.015	0.015	0	0	1	1	0	11	1	1.1	0.9;
];

mpc.gen = [
	1	0	0	10	-10	1	100	1	10	0	0	0	0	0	0	0	0	0	0	0	0;
];

mpc.branch = [
	1	2	0.00903305785123967	0.003760330578512397	0	0	0	0	0	0	1	-360	360;
	2	3	0.00978512396694215	0.004082644628099173	0	0	0	0	0	0	1	-360	360;
	3	4	0.01731404958677686	0.007214876033057851	0	0	0	0	0	0	1	-360	360;
	4	5	0.02634710743801653	0.010983471074380165	0	0	0	0	0	0	1	-360	360;
	5	6	0.00903305785123967	0.003760330578512397	0	0	0	0	0	0	1	-360	360;
	6	7	0.00828099173553719	0.003446280991735537	0	0	0	0	0	0	1	-360	360;
	7	8	0.03638842975206611	0.010041322314049589	0	0	0	0	0	0	1	-360	360;
	8	9	0.046628099173553726	0.013198347107438016	0	0	0	0	0	0	1	-360	360;
	9	10	0.02388429752066116	0.006760330578512396	0	0	0	0	0	0	1	-360	360;
	10	11	0.012512396694214877	0.003537190082644628	0	0	0	0	0	0	1	-360	360;
	11	12	0.010231404958677685	0.0029008264462809918	0	0	0	0	0	0	1	-360	360;
];

mpc.gencost = [
	2	0	0	3	0	20	0;
];
