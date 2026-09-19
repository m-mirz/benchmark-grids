function mpc = case18nbr
%CASE18NBR  Power flow data for 18 bus distribution system from Battu, et al
%   Please see CASEFORMAT for details on the case file format.
%
%   Data from ...
%       Battu NR, Abhyankar AR, Senroy N (2016) DG Planning with Amalgamation
%       of Operational and Reliability Considerations. Int J Emerg Electr
%       Power Syst 17:131-141. doi: 10.1515/ijeeps-2015-0142
%       URL: https://doi.org/10.1515/ijeeps-2015-0142
%
%   Plain-data copy of benchmark-grids/matpower/case18nbr.m: the file's
%   MATLAB statements (below, as they were) are evaluated by
%   scripts/evaluate_matpower_code.py and the matrices hold the result.
%     mpc.bus(:, [PD, QD]) = mpc.bus(:, [PD, QD]) / 1e3;

%% MATPOWER Case Format : Version 2
mpc.version = '2';

mpc.baseMVA = 100;

mpc.bus = [
	1	3	0	0	0	0	1	1	0	11	1	1	1;
	2	1	0.0441	0.045	0	0	1	1	0	11	1	1.1	0.9;
	3	1	0.07	0.0714	0	0	1	1	0	11	1	1.1	0.9;
	4	1	0.14	0.1428	0	0	1	1	0	11	1	1.1	0.9;
	5	1	0.0441	0.045	0	0	1	1	0	11	1	1.1	0.9;
	6	1	0.14	0.1428	0	0	1	1	0	11	1	1.1	0.9;
	7	1	0.14	0.1428	0	0	1	1	0	11	1	1.1	0.9;
	8	1	0.07	0.0714	0	0	1	1	0	11	1	1.1	0.9;
	9	1	0.07	0.0714	0	0	1	1	0	11	1	1.1	0.9;
	10	1	0.0441	0.045	0	0	1	1	0	11	1	1.1	0.9;
	11	1	0.14	0.1428	0	0	1	1	0	11	1	1.1	0.9;
	12	1	0.07	0.0714	0	0	1	1	0	11	1	1.1	0.9;
	13	1	0.0441	0.045	0	0	1	1	0	11	1	1.1	0.9;
	14	1	0.07	0.0714	0	0	1	1	0	11	1	1.1	0.9;
	15	1	0.14	0.1428	0	0	1	1	0	11	1	1.1	0.9;
	16	1	0.07	0.0714	0	0	1	1	0	11	1	1.1	0.9;
	17	1	0.07	0.0714	0	0	1	1	0	11	1	1.1	0.9;
	18	1	0.0441	0.045	0	0	1	1	0	11	1	1.1	0.9;
];

mpc.gen = [
	1	0	0	10	-10	1	100	1	10	0	0	0	0	0	0	0	0	0	0	0	0;
];

mpc.branch = [
	1	2	0.7766	0.7596	0	0	0	0	0	0	1	-360	360;
	2	3	0.6716	0.6569	0	0	0	0	0	0	1	-360	360;
	3	4	0.4827	0.4722	0	0	0	0	0	0	1	-360	360;
	4	5	0.8744	0.5898	0	0	0	0	0	0	1	-360	360;
	2	9	1.1554	0.7793	0	0	0	0	0	0	1	-360	360;
	9	10	0.968	0.6529	0	0	0	0	0	0	1	-360	360;
	2	6	1.4677	0.99	0	0	0	0	0	0	1	-360	360;
	6	7	0.6245	0.4213	0	0	0	0	0	0	1	-360	360;
	6	8	0.7182	0.4844	0	0	0	0	0	0	1	-360	360;
	3	11	1.0305	0.6951	0	0	0	0	0	0	1	-360	360;
	11	12	1.4052	0.9478	0	0	0	0	0	0	1	-360	360;
	12	13	1.1554	0.7793	0	0	0	0	0	0	1	-360	360;
	4	14	1.2803	0.8636	0	0	0	0	0	0	1	-360	360;
	4	15	0.687	0.4634	0	0	0	0	0	0	1	-360	360;
	5	16	0.6245	0.4213	0	0	0	0	0	0	1	-360	360;
	16	17	0.7182	0.4844	0	0	0	0	0	0	1	-360	360;
	17	18	0.7182	0.4844	0	0	0	0	0	0	1	-360	360;
];

mpc.gencost = [
	2	0	0	3	0	20	0;
];
