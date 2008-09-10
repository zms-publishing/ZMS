<?xml version="1.0" encoding="UTF-8"?>
<structure version="2" schemafile="OrgChart.xsd" workingxmlfile="OrgChart.xml" templatexmlfile="">
	<nspair prefix="n1" uri="http://www.xmlspy.com/schemas/orgchart"/>
	<nspair prefix="ipo" uri="http://www.altova.com/IPO"/>
	<nspair prefix="xsi" uri="http://www.w3.org/2001/XMLSchema-instance"/>
	<textstateicon match="bold" iconfile="bold.bmp"/>
	<textstateicon match="italic" iconfile="italic.bmp"/>
	<template>
		<match overwrittenxslmatch="/"/>
		<children>
			<template>
				<match match="n1:OrgChart"/>
				<children>
					<template>
						<editorproperties adding="mandatory" autoaddname="1" editable="1" markupmode="hide"/>
						<match match="n1:CompanyLogo"/>
						<children>
							<paragraph paragraphtag="div">
								<styles border-bottom-color="#0588BA" border-bottom-style="solid" border-bottom-width="medium" border-width="4pt" padding-bottom="10px" padding-left="10px"/>
								<children>
									<template>
										<editorproperties adding="mandatory" autoaddname="1" editable="1" markupmode="hide" userinfo="To change the logo, key in a new location below."/>
										<match match="@href"/>
										<children>
											<link>
												<hyperlink>
													<fixtext value="http://www.nanonull.com/"/>
												</hyperlink>
												<children>
													<image>
														<properties border="0"/>
														<imagesource>
															<xpath value="."/>
														</imagesource>
													</image>
												</children>
											</link>
										</children>
									</template>
								</children>
							</paragraph>
						</children>
					</template>
					<newline/>
					<template>
						<match match="n1:Name"/>
						<children>
							<xpath allchildren="1">
								<styles color="#0588BA" font-family="Arial" font-size="20pt" font-weight="bold"/>
							</xpath>
						</children>
					</template>
					<newline/>
					<newline/>
					<template>
						<match match="n1:Office"/>
						<children>
							<newline/>
							<paragraph paragraphtag="div">
								<styles border-top-color="#0588ba" border-top-style="solid" border-top-width="2pt"/>
								<children>
									<newline/>
									<template>
										<match match="n1:Name"/>
										<children>
											<xpath allchildren="1">
												<styles color="#707070" font-family="Arial" font-size="15pt" font-weight="bold"/>
											</xpath>
										</children>
									</template>
									<newline/>
									<newline/>
									<text fixtext="Location: ">
										<styles color="#808080" font-family="Arial" font-size="smaller" font-weight="bold"/>
									</text>
									<choice>
										<children>
											<choiceoption>
												<testexpression>
													<xpath value="not(n1:Address or  n1:Address_EU)"/>
												</testexpression>
												<children>
													<template>
														<editorproperties adding="mandatory" autoaddname="1" editable="1" markupmode="hide" userinfo="After you add the address element corresponding to your Location selection, the Location field becomes non-editable."/>
														<match match="n1:Location"/>
														<children>
															<select ownvalue="1">
																<properties size="0"/>
																<editorproperties adding="mandatory" autoaddname="1" editable="1" markupmode="hide"/>
																<selectoption description="US" value="US"/>
																<selectoption description="EU" value="EU"/>
															</select>
														</children>
													</template>
												</children>
											</choiceoption>
											<choiceoption>
												<children>
													<template>
														<editorproperties adding="mandatory" autoaddname="1" editable="0" markupmode="hide" userinfo="To edit this field, the Address element of this Office element will have to be deleted using a Text View of the document."/>
														<match match="n1:Location"/>
														<children>
															<xpath allchildren="1">
																<styles color="#808080" font-weight="bold"/>
															</xpath>
														</children>
													</template>
												</children>
											</choiceoption>
										</children>
									</choice>
								</children>
							</paragraph>
							<table>
								<properties border="1" cellspacing="0" width="100%"/>
								<children>
									<tablebody>
										<children>
											<tablerow>
												<children>
													<tablecol>
														<properties valign="top" width="60%"/>
														<children>
															<choice>
																<children>
																	<choiceoption>
																		<testexpression>
																			<xpath value="n1:Location =&quot;US&quot;"/>
																		</testexpression>
																		<children>
																			<template>
																				<match match="n1:Address"/>
																				<children>
																					<table>
																						<properties border="0" cellspacing="4px" width="100%"/>
																						<children>
																							<tablebody>
																								<children>
																									<tablerow>
																										<children>
																											<tablecol>
																												<properties width="30%"/>
																												<children>
																													<text fixtext="Street: ">
																														<styles font-weight="bold"/>
																													</text>
																												</children>
																											</tablecol>
																											<tablecol>
																												<properties width="70%"/>
																												<children>
																													<template>
																														<match match="ipo:street"/>
																														<children>
																															<xpath allchildren="1"/>
																														</children>
																													</template>
																												</children>
																											</tablecol>
																										</children>
																									</tablerow>
																									<tablerow>
																										<children>
																											<tablecol>
																												<properties width="30%"/>
																												<children>
																													<text fixtext="City:">
																														<styles font-weight="bold"/>
																													</text>
																												</children>
																											</tablecol>
																											<tablecol>
																												<properties width="70%"/>
																												<children>
																													<template>
																														<match match="ipo:city"/>
																														<children>
																															<xpath allchildren="1"/>
																														</children>
																													</template>
																												</children>
																											</tablecol>
																										</children>
																									</tablerow>
																									<tablerow>
																										<children>
																											<tablecol>
																												<properties width="30%"/>
																												<children>
																													<text fixtext="State &amp; Zip:">
																														<styles font-weight="bold"/>
																													</text>
																												</children>
																											</tablecol>
																											<tablecol>
																												<properties width="70%"/>
																												<children>
																													<template>
																														<match match="ipo:state"/>
																														<children>
																															<select ownvalue="1" enumeration="1">
																																<properties size="0"/>
																															</select>
																														</children>
																													</template>
																													<text fixtext=" "/>
																													<template>
																														<match match="ipo:zip"/>
																														<children>
																															<field ownvalue="1">
																																<properties value=""/>
																															</field>
																														</children>
																													</template>
																												</children>
																											</tablecol>
																										</children>
																									</tablerow>
																								</children>
																							</tablebody>
																						</children>
																					</table>
																				</children>
																			</template>
																		</children>
																	</choiceoption>
																	<choiceoption>
																		<testexpression>
																			<xpath value="n1:Location =&quot;EU&quot;"/>
																		</testexpression>
																		<children>
																			<template>
																				<match match="n1:Address_EU"/>
																				<children>
																					<table>
																						<properties border="0" cellspacing="4px" width="100%"/>
																						<children>
																							<tablebody>
																								<children>
																									<tablerow>
																										<children>
																											<tablecol>
																												<properties width="30%"/>
																												<children>
																													<text fixtext="Street:">
																														<styles font-weight="bold"/>
																													</text>
																												</children>
																											</tablecol>
																											<tablecol>
																												<properties width="70%"/>
																												<children>
																													<template>
																														<match match="ipo:street"/>
																														<children>
																															<field ownvalue="1">
																																<properties value=""/>
																															</field>
																														</children>
																													</template>
																												</children>
																											</tablecol>
																										</children>
																									</tablerow>
																									<tablerow>
																										<children>
																											<tablecol>
																												<properties width="30%"/>
																												<children>
																													<text fixtext="City:">
																														<styles font-weight="bold"/>
																													</text>
																												</children>
																											</tablecol>
																											<tablecol>
																												<properties width="70%"/>
																												<children>
																													<template>
																														<match match="ipo:city"/>
																														<children>
																															<field ownvalue="1">
																																<properties value=""/>
																															</field>
																														</children>
																													</template>
																												</children>
																											</tablecol>
																										</children>
																									</tablerow>
																									<tablerow>
																										<children>
																											<tablecol>
																												<properties width="30%"/>
																												<children>
																													<text fixtext="Post Code:">
																														<styles font-weight="bold"/>
																													</text>
																												</children>
																											</tablecol>
																											<tablecol>
																												<properties width="70%"/>
																												<children>
																													<template>
																														<match match="ipo:postcode"/>
																														<children>
																															<field ownvalue="1">
																																<properties value=""/>
																															</field>
																														</children>
																													</template>
																												</children>
																											</tablecol>
																										</children>
																									</tablerow>
																								</children>
																							</tablebody>
																						</children>
																					</table>
																				</children>
																			</template>
																		</children>
																	</choiceoption>
																</children>
															</choice>
														</children>
													</tablecol>
													<tablecol>
														<properties valign="top" width="40%"/>
														<children>
															<table>
																<properties border="0" cellspacing="4" width="100%"/>
																<children>
																	<tablebody>
																		<children>
																			<tablerow>
																				<children>
																					<tablecol>
																						<properties width="25%"/>
																						<children>
																							<text fixtext="Phone:">
																								<styles font-weight="bold"/>
																							</text>
																						</children>
																					</tablecol>
																					<tablecol>
																						<properties width="75%"/>
																						<children>
																							<template>
																								<match match="n1:Phone"/>
																								<children>
																									<xpath allchildren="1"/>
																								</children>
																							</template>
																						</children>
																					</tablecol>
																				</children>
																			</tablerow>
																			<tablerow>
																				<children>
																					<tablecol>
																						<properties width="25%"/>
																						<children>
																							<text fixtext="Fax:">
																								<styles font-weight="bold"/>
																							</text>
																						</children>
																					</tablecol>
																					<tablecol>
																						<properties width="75%"/>
																						<children>
																							<template>
																								<editorproperties adding="mandatory" autoaddname="1" editable="1" markupmode="hide"/>
																								<match match="n1:Fax"/>
																								<children>
																									<xpath allchildren="1">
																										<editorproperties adding="mandatory" autoaddname="1" editable="1" markupmode="hide"/>
																									</xpath>
																								</children>
																							</template>
																						</children>
																					</tablecol>
																				</children>
																			</tablerow>
																			<tablerow>
																				<children>
																					<tablecol>
																						<properties width="25%"/>
																						<children>
																							<text fixtext="E-mail:">
																								<styles font-weight="bold"/>
																							</text>
																						</children>
																					</tablecol>
																					<tablecol>
																						<properties width="75%"/>
																						<children>
																							<template>
																								<match match="n1:EMail"/>
																								<children>
																									<link>
																										<hyperlink>
																											<fixtext value="mailto:"/>
																											<xpath value="."/>
																										</hyperlink>
																										<children>
																											<xpath allchildren="1"/>
																										</children>
																									</link>
																								</children>
																							</template>
																						</children>
																					</tablecol>
																				</children>
																			</tablerow>
																		</children>
																	</tablebody>
																</children>
															</table>
														</children>
													</tablecol>
												</children>
											</tablerow>
										</children>
									</tablebody>
								</children>
							</table>
							<newline/>
							<choice>
								<children>
									<choiceoption>
										<testexpression>
											<xpath value="n1:Address"/>
										</testexpression>
										<children>
											<template>
												<styles color="#004080" font-family="Arial" font-size="10pt" font-weight="bold"/>
												<match match="n1:Address"/>
												<children>
													<template>
														<editorproperties adding="mandatory" autoaddname="1" editable="0" markupmode="hide"/>
														<match match="ipo:city"/>
														<children>
															<xpath allchildren="1">
																<styles color="#004080" font-family="Arial" font-size="10pt" font-weight="bold" text-decoration="underline"/>
															</xpath>
														</children>
													</template>
												</children>
											</template>
										</children>
									</choiceoption>
									<choiceoption>
										<testexpression>
											<xpath value="n1:Address_EU"/>
										</testexpression>
										<children>
											<template>
												<match match="n1:Address_EU"/>
												<children>
													<template>
														<editorproperties adding="mandatory" autoaddname="1" editable="0" markupmode="hide"/>
														<match match="ipo:city"/>
														<children>
															<xpath allchildren="1">
																<styles color="#004080" font-family="Arial" font-size="10pt" font-weight="bold" text-decoration="underline"/>
															</xpath>
														</children>
													</template>
												</children>
											</template>
										</children>
									</choiceoption>
								</children>
							</choice>
							<text fixtext=" Office Summary:">
								<styles color="#004080" font-family="Arial" font-size="10pt" font-weight="bold" text-decoration="underline"/>
							</text>
							<text fixtext="  "/>
							<autovalue>
								<styles color="#004080" font-family="Arial" font-size="10pt" font-weight="bold"/>
								<editorproperties editable="0"/>
								<autocalc>
									<xpath value="count(n1:Department)"/>
								</autocalc>
							</autovalue>
							<text fixtext=" department">
								<styles color="#004080" font-family="Arial" font-size="10pt" font-weight="bold"/>
							</text>
							<choice>
								<children>
									<choiceoption>
										<testexpression>
											<xpath value="count(n1:Department) != 1"/>
										</testexpression>
										<children>
											<text fixtext="s">
												<styles color="#004080" font-family="Arial" font-size="10pt" font-weight="bold"/>
											</text>
										</children>
									</choiceoption>
								</children>
							</choice>
							<text fixtext=", ">
								<styles color="#004080" font-family="Arial" font-size="10pt" font-weight="bold"/>
							</text>
							<autovalue>
								<styles color="#004080" font-family="Arial" font-size="10pt" font-weight="bold"/>
								<editorproperties editable="0"/>
								<autocalc>
									<xpath value="count(n1:Department/n1:Person)"/>
								</autocalc>
							</autovalue>
							<text fixtext=" employee">
								<styles color="#004080" font-family="Arial" font-size="10pt" font-weight="bold"/>
							</text>
							<choice>
								<children>
									<choiceoption>
										<testexpression>
											<xpath value="count(n1:Department/n1:Person) != 1"/>
										</testexpression>
										<children>
											<text fixtext="s">
												<styles color="#004080" font-family="Arial" font-size="10pt" font-weight="bold"/>
											</text>
										</children>
									</choiceoption>
								</children>
							</choice>
							<text fixtext=".">
								<styles color="#004080" font-family="Arial" font-size="10pt" font-weight="bold"/>
							</text>
							<template>
								<match match="n1:Desc"/>
								<children>
									<template>
										<match match="n1:para"/>
										<children>
											<paragraph paragraphtag="p">
												<children>
													<xpath allchildren="1"/>
												</children>
											</paragraph>
										</children>
									</template>
								</children>
							</template>
							<template>
								<match match="n1:Department"/>
								<children>
									<newline/>
									<template>
										<match match="n1:Name"/>
										<children>
											<xpath allchildren="1">
												<styles color="#D39658" font-family="Arial" font-weight="bold"/>
											</xpath>
										</children>
									</template>
									<text fixtext="  "/>
									<text>
										<styles color="#D39658"/>
									</text>
									<text fixtext="( ">
										<styles color="#D39658" font-family="Arial" font-weight="bold"/>
									</text>
									<autovalue>
										<styles color="#D39658" font-family="Arial" font-weight="bold"/>
										<editorproperties editable="0"/>
										<autocalc>
											<xpath value="count(n1:Person)"/>
										</autocalc>
									</autovalue>
									<text fixtext=" )">
										<styles color="#D39658" font-family="Arial" font-weight="bold"/>
									</text>
									<newline/>
									<template>
										<match match="n1:Person"/>
										<children>
											<table dynamic="1">
												<properties border="1" cellpadding="3" cellspacing="0" width="100%"/>
												<children>
													<tableheader>
														<children>
															<tablerow>
																<properties bgcolor="#D2C8AE"/>
																<children>
																	<tablecol>
																		<properties align="center" bgcolor="#D2C8AE" rowspan="2" width="10%"/>
																		<children>
																			<text fixtext="First">
																				<styles color="#606060" font-family="Arial" font-weight="bold"/>
																			</text>
																		</children>
																	</tablecol>
																	<tablecol>
																		<properties align="center" bgcolor="#D2C8AE" rowspan="2" width="12%"/>
																		<children>
																			<text fixtext="Last">
																				<styles color="#606060" font-family="Arial" font-weight="bold"/>
																			</text>
																		</children>
																	</tablecol>
																	<tablecol>
																		<properties align="center" bgcolor="#D2C8AE" rowspan="2" width="16%"/>
																		<children>
																			<text fixtext="Title">
																				<styles color="#606060" font-family="Arial" font-weight="bold"/>
																			</text>
																		</children>
																	</tablecol>
																	<tablecol>
																		<properties align="center" bgcolor="#D2C8AE" rowspan="2" width="5%"/>
																		<children>
																			<text fixtext="Ext">
																				<styles color="#606060" font-family="Arial" font-weight="bold"/>
																			</text>
																		</children>
																	</tablecol>
																	<tablecol>
																		<properties align="center" bgcolor="#D2C8AE" rowspan="2" width="23%"/>
																		<children>
																			<text fixtext="EMail">
																				<styles color="#606060" font-family="Arial" font-weight="bold"/>
																			</text>
																		</children>
																	</tablecol>
																	<tablecol>
																		<properties align="center" bgcolor="#D2C8AE" rowspan="2" width="10%"/>
																		<children>
																			<text fixtext="Shares">
																				<styles color="#606060" font-family="Arial" font-weight="bold"/>
																			</text>
																		</children>
																	</tablecol>
																	<tablecol>
																		<properties align="center" colspan="3" width="8%"/>
																		<children>
																			<text fixtext="Leave">
																				<styles color="#606060" font-family="Arial" font-weight="bold"/>
																			</text>
																		</children>
																	</tablecol>
																</children>
															</tablerow>
															<tablerow>
																<children>
																	<tablecol>
																		<properties align="center" bgcolor="#D2C8AE" width="8%"/>
																		<children>
																			<text fixtext="Total">
																				<styles color="#606060" font-family="Arial" font-weight="bold"/>
																			</text>
																		</children>
																	</tablecol>
																	<tablecol>
																		<properties align="center" bgcolor="#D2C8AE" width="8%"/>
																		<children>
																			<text fixtext="Used">
																				<styles color="#606060" font-family="Arial" font-weight="bold"/>
																			</text>
																		</children>
																	</tablecol>
																	<tablecol>
																		<properties align="center" bgcolor="#D2C8AE" width="8%"/>
																		<children>
																			<text fixtext="Left">
																				<styles color="#606060" font-family="Arial" font-weight="bold"/>
																			</text>
																		</children>
																	</tablecol>
																</children>
															</tablerow>
														</children>
													</tableheader>
													<tablefooter>
														<children>
															<tablerow>
																<properties bgcolor="#F2F0E6"/>
																<children>
																	<tablecol>
																		<properties align="left" colspan="5" valign="top" width="23%"/>
																		<children>
																			<text fixtext="Employees:  ">
																				<styles color="#004080" font-family="Arial" font-size="8pt" font-weight="bold"/>
																			</text>
																			<autovalue>
																				<styles color="#004080" font-family="Arial" font-size="8pt" font-weight="bold"/>
																				<editorproperties editable="0"/>
																				<autocalc>
																					<xpath value="count(  n1:Person  )"/>
																				</autocalc>
																			</autovalue>
																			<text fixtext=" ">
																				<styles font-size="8pt"/>
																			</text>
																			<text fixtext="(">
																				<styles color="#004080" font-family="Arial" font-size="8pt" font-weight="bold"/>
																			</text>
																			<autovalue>
																				<styles color="#004080" font-family="Arial" font-size="8pt" font-weight="bold"/>
																				<editorproperties editable="0"/>
																				<autocalc>
																					<xpath value="round ((count(  n1:Person  ) ) div ( count( ../n1:Department/ n1:Person  ) ) * 100)"/>
																				</autocalc>
																			</autovalue>
																			<text fixtext="% of Office, ">
																				<styles color="#004080" font-family="Arial" font-size="8pt" font-weight="bold"/>
																			</text>
																			<autovalue>
																				<styles color="#004080" font-family="Arial" font-size="8pt" font-weight="bold"/>
																				<editorproperties editable="0"/>
																				<autocalc>
																					<xpath value="round ((count(  n1:Person  ) ) div ( count( ../../n1:Office/n1:Department/ n1:Person  ) ) * 100)"/>
																				</autocalc>
																			</autovalue>
																			<text fixtext="% of Company)">
																				<styles color="#004080" font-family="Arial" font-size="8pt" font-weight="bold"/>
																			</text>
																		</children>
																	</tablecol>
																	<tablecol>
																		<properties align="left" colspan="4" width="10%"/>
																		<children>
																			<text fixtext="Shares: ">
																				<styles color="#004080" font-family="Arial" font-size="8pt" font-weight="bold"/>
																			</text>
																			<autovalue>
																				<styles color="#004080" font-family="Arial" font-size="8pt" font-weight="bold"/>
																				<editorproperties editable="0"/>
																				<autocalc>
																					<xpath value="sum(  n1:Person/n1:Shares  )"/>
																				</autocalc>
																			</autovalue>
																			<text fixtext=" ">
																				<styles font-size="8pt"/>
																			</text>
																			<text fixtext="(">
																				<styles color="#004080" font-family="Arial" font-size="8pt" font-weight="bold"/>
																			</text>
																			<autovalue>
																				<styles color="#004080" font-family="Arial" font-size="8pt" font-weight="bold"/>
																				<editorproperties editable="0"/>
																				<autocalc>
																					<xpath value="round((sum(  n1:Person/n1:Shares  ) ) div (sum(../n1:Department/ n1:Person/n1:Shares ) ) * 100)"/>
																				</autocalc>
																			</autovalue>
																			<text fixtext="% of Office, ">
																				<styles color="#004080" font-family="Arial" font-size="8pt" font-weight="bold"/>
																			</text>
																			<autovalue>
																				<styles color="#004080" font-family="Arial" font-size="8pt" font-weight="bold"/>
																				<editorproperties editable="0"/>
																				<autocalc>
																					<xpath value="round((sum(  n1:Person/n1:Shares  ) ) div (sum(../../n1:Office/n1:Department/ n1:Person/n1:Shares  )) * 100)"/>
																				</autocalc>
																			</autovalue>
																			<text fixtext="% of Company)">
																				<styles color="#004080" font-family="Arial" font-size="8pt" font-weight="bold"/>
																			</text>
																		</children>
																	</tablecol>
																</children>
															</tablerow>
															<tablerow>
																<properties bgcolor="#F2F0E6"/>
																<children>
																	<tablecol>
																		<properties align="left" colspan="13" width="23%"/>
																		<children>
																			<text fixtext="Non-Shareholders: ">
																				<styles color="#004080" font-family="Arial" font-size="8pt" font-weight="bold"/>
																			</text>
																			<text fixtext=" ">
																				<styles color="#004040" font-family="Arial" font-size="8pt" font-weight="bold"/>
																			</text>
																			<template>
																				<editorproperties adding="mandatory" autoaddname="1" editable="0" markupmode="hide"/>
																				<match match="n1:Person"/>
																				<children>
																					<choice>
																						<children>
																							<choiceoption>
																								<testexpression>
																									<xpath value="n1:Shares &lt;= 0 or not (n1:Shares)"/>
																								</testexpression>
																								<children>
																									<template>
																										<match match="n1:First"/>
																										<children>
																											<xpath allchildren="1">
																												<styles color="#004040" font-family="Arial" font-size="8pt" font-weight="bold"/>
																											</xpath>
																										</children>
																									</template>
																									<text fixtext=" ">
																										<styles color="#004040" font-family="Arial" font-size="8pt" font-weight="bold"/>
																									</text>
																									<template>
																										<match match="n1:Last"/>
																										<children>
																											<xpath allchildren="1">
																												<styles color="#004040" font-family="Arial" font-size="8pt" font-weight="bold"/>
																											</xpath>
																										</children>
																									</template>
																									<choice>
																										<children>
																											<choiceoption>
																												<testexpression>
																													<xpath value="following-sibling::n1:Person[n1:Shares&lt;=0 or not(n1:Shares)]"/>
																												</testexpression>
																												<children>
																													<text fixtext=", ">
																														<styles color="#004040" font-family="Arial" font-size="8pt" font-weight="bold"/>
																													</text>
																												</children>
																											</choiceoption>
																										</children>
																									</choice>
																								</children>
																							</choiceoption>
																						</children>
																					</choice>
																				</children>
																			</template>
																			<choice>
																				<styles color="#004080" font-family="Arial" font-size="10pt" font-weight="bold"/>
																				<children>
																					<choiceoption>
																						<testexpression>
																							<xpath value="count(  n1:Person  ) = count(  n1:Person [n1:Shares&gt;0] )"/>
																						</testexpression>
																						<children>
																							<text fixtext="None">
																								<styles color="#004040" font-family="Arial" font-size="8pt" font-weight="bold"/>
																							</text>
																						</children>
																					</choiceoption>
																				</children>
																			</choice>
																			<text fixtext=".">
																				<styles color="#004040" font-family="Arial" font-size="8pt" font-weight="bold"/>
																			</text>
																		</children>
																	</tablecol>
																</children>
															</tablerow>
														</children>
													</tablefooter>
													<tablebody>
														<children>
															<tablerow>
																<children>
																	<tablecol>
																		<properties width="10%"/>
																		<children>
																			<template>
																				<match match="n1:First"/>
																				<children>
																					<choice>
																						<children>
																							<choiceoption>
																								<testexpression>
																									<xpath value="../n1:Shares &gt; 0"/>
																								</testexpression>
																								<children>
																									<xpath allchildren="1">
																										<styles font-size="10pt" font-weight="bold"/>
																									</xpath>
																								</children>
																							</choiceoption>
																							<choiceoption>
																								<children>
																									<xpath allchildren="1">
																										<styles font-size="10pt"/>
																									</xpath>
																								</children>
																							</choiceoption>
																						</children>
																					</choice>
																				</children>
																			</template>
																		</children>
																	</tablecol>
																	<tablecol>
																		<properties width="12%"/>
																		<children>
																			<template>
																				<match match="n1:Last"/>
																				<children>
																					<choice>
																						<children>
																							<choiceoption>
																								<testexpression>
																									<xpath value="../n1:Shares &gt; 0"/>
																								</testexpression>
																								<children>
																									<xpath allchildren="1">
																										<styles font-size="10pt" font-weight="bold"/>
																									</xpath>
																								</children>
																							</choiceoption>
																							<choiceoption>
																								<children>
																									<xpath allchildren="1">
																										<styles font-size="10pt"/>
																									</xpath>
																								</children>
																							</choiceoption>
																						</children>
																					</choice>
																				</children>
																			</template>
																		</children>
																	</tablecol>
																	<tablecol>
																		<properties width="16%"/>
																		<children>
																			<template>
																				<editorproperties adding="mandatory" autoaddname="1" editable="1" markupmode="hide"/>
																				<match match="n1:Title"/>
																				<children>
																					<xpath allchildren="1">
																						<styles font-size="10pt"/>
																					</xpath>
																				</children>
																			</template>
																		</children>
																	</tablecol>
																	<tablecol>
																		<properties align="center" width="5%"/>
																		<children>
																			<template>
																				<match match="n1:PhoneExt"/>
																				<children>
																					<xpath allchildren="1">
																						<styles font-size="10pt"/>
																						<editorproperties adding="mandatory" autoaddname="1" editable="1" markupmode="hide"/>
																						<addvalidations>
																							<addvalidation>
																								<usermsg>Telephone extensions must be 3 digits long.</usermsg>
																								<xpath value="string-length(.) = 3"/>
																							</addvalidation>
																						</addvalidations>
																					</xpath>
																				</children>
																			</template>
																		</children>
																	</tablecol>
																	<tablecol>
																		<properties width="23%"/>
																		<children>
																			<template>
																				<match match="n1:EMail"/>
																				<children>
																					<link>
																						<hyperlink>
																							<fixtext value="mailto:"/>
																							<xpath value="."/>
																						</hyperlink>
																						<children>
																							<xpath allchildren="1">
																								<styles font-size="10pt"/>
																							</xpath>
																						</children>
																					</link>
																				</children>
																			</template>
																		</children>
																	</tablecol>
																	<tablecol>
																		<properties align="center" width="10%"/>
																		<children>
																			<template>
																				<match match="n1:Shares"/>
																				<children>
																					<xpath allchildren="1">
																						<styles font-size="10pt"/>
																					</xpath>
																				</children>
																			</template>
																		</children>
																	</tablecol>
																	<tablecol>
																		<properties align="center" width="8%"/>
																		<children>
																			<template>
																				<match match="n1:LeaveTotal"/>
																				<children>
																					<xpath allchildren="1">
																						<styles font-size="10pt"/>
																					</xpath>
																				</children>
																			</template>
																		</children>
																	</tablecol>
																	<tablecol>
																		<properties align="center" width="8%"/>
																		<children>
																			<template>
																				<match match="n1:LeaveUsed"/>
																				<children>
																					<xpath allchildren="1">
																						<styles font-size="10pt"/>
																					</xpath>
																				</children>
																			</template>
																		</children>
																	</tablecol>
																	<tablecol>
																		<properties align="center" width="8%"/>
																		<children>
																			<autovalue>
																				<styles font-size="10pt"/>
																				<editorproperties editable="0"/>
																				<autocalc>
																					<xpath value="n1:LeaveTotal - n1:LeaveUsed"/>
																					<update>
																						<xpath value="n1:LeaveLeft"/>
																					</update>
																				</autocalc>
																			</autovalue>
																		</children>
																	</tablecol>
																</children>
															</tablerow>
														</children>
													</tablebody>
												</children>
											</table>
										</children>
									</template>
									<newline/>
								</children>
							</template>
						</children>
					</template>
					<newline/>
				</children>
			</template>
		</children>
	</template>
	<template>
		<match match="n1:bold"/>
		<children>
			<xpath allchildren="1">
				<styles font-weight="bold"/>
			</xpath>
		</children>
	</template>
	<template>
		<match match="n1:italic"/>
		<children>
			<xpath allchildren="1">
				<styles font-style="italic"/>
			</xpath>
		</children>
	</template>
	<pagelayout>
		<properties pagemultiplepages="0" pagenumberingformat="1" pagenumberingstartat="1" paperheight="11in" papermarginbottom="0.79in" papermarginleft="0.6in" papermarginright="0.6in" papermargintop="0.79in" paperwidth="8.5in"/>
	</pagelayout>
</structure>
